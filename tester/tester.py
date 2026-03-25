#!/usr/bin/env python3
# ============================================================
#  Webserv 42 — HTTP Parser Tester
#  Config associée : tester.conf
#
#  Vhost localhost  (Host: localhost)  → port 8080
#    /              GET only
#    /contacts      GET POST DELETE
#
#  Vhost rshin      (Host: rshin)      → port 8080
#    /upload        POST only
#    /delete        DELETE only
#
#  Format expected :
#    int         → un seul code accepté
#    (int, ...)  → plusieurs codes acceptés
# ============================================================
import socket
import time

HOST = "127.0.0.1"
PORT = 8080

tests = [
    # ──────────────────────────────────────────────────────
    # VALID — vhost localhost
    # ──────────────────────────────────────────────────────

    # GET / → index.html → 200
    ("VALID_GET",
     200,
     "GET / HTTP/1.1\r\nHost: localhost\r\n\r\n"),

    # GET avec query string → / existe → 200, query ignorée par le serveur
    ("VALID_GET_QUERY_STRING",
     (200, 404),
     "GET /search?q=hello&page=1 HTTP/1.1\r\nHost: localhost\r\n\r\n"),

    # GET URI percent-encodée → path inconnu → 404
    ("VALID_GET_ENCODED_URI",
     (200, 404),
     "GET /path%20with%20spaces HTTP/1.1\r\nHost: localhost\r\n\r\n"),

    # GET avec plusieurs headers — doit répondre normalement
    ("VALID_GET_MULTIPLE_HEADERS",
     200,
     "GET / HTTP/1.1\r\nHost: localhost\r\nAccept: text/html\r\nAccept-Language: fr-FR\r\nConnection: keep-alive\r\n\r\n"),

    # POST /contacts → route configurée → 200 ou 201
    ("VALID_POST_CONTACTS",
     (200, 201),
     "POST /contacts HTTP/1.1\r\nHost: localhost\r\nContent-Length: 5\r\n\r\nhello"),

    # POST /contacts body vide → valide
    ("VALID_POST_CONTACTS_EMPTY_BODY",
     (200, 201),
     "POST /contacts HTTP/1.1\r\nHost: localhost\r\nContent-Length: 0\r\n\r\n"),

    # DELETE /contacts → route configurée → 200 ou 204
    ("VALID_DELETE_CONTACTS",
     (200, 204, 404),
     "DELETE /contacts HTTP/1.1\r\nHost: localhost\r\n\r\n"),

    # ──────────────────────────────────────────────────────
    # VALID — vhost rshin (Host: rshin)
    # ──────────────────────────────────────────────────────

    # POST /upload → route configurée sur rshin → 200 ou 201
    ("VALID_POST_UPLOAD_RSHIN",
     (200, 201),
     "POST /upload HTTP/1.1\r\nHost: rshin\r\nContent-Type: application/octet-stream\r\nContent-Length: 4\r\n\r\ndata"),

    # DELETE /delete → route configurée sur rshin → 200 ou 204
    ("VALID_DELETE_RSHIN",
     (200, 204, 404),
     "DELETE /delete HTTP/1.1\r\nHost: rshin\r\n\r\n"),

    # GET / sur rshin → 200
    ("VALID_GET_RSHIN",
     200,
     "GET / HTTP/1.1\r\nHost: rshin\r\n\r\n"),

    # ──────────────────────────────────────────────────────
    # MÉTHODES non autorisées
    # ──────────────────────────────────────────────────────

    # POST / → allowed_methods GET seulement → 405
    ("METHOD_POST_ON_ROOT_NOT_ALLOWED",
     405,
     "POST / HTTP/1.1\r\nHost: localhost\r\nContent-Length: 5\r\n\r\nhello"),

    # DELETE / → allowed_methods GET seulement → 405
    ("METHOD_DELETE_ON_ROOT_NOT_ALLOWED",
     405,
     "DELETE / HTTP/1.1\r\nHost: localhost\r\n\r\n"),

    # POST /upload sur localhost → upload n'existe que sur rshin → 404 ou 405
    ("METHOD_POST_UPLOAD_WRONG_VHOST",
     (404, 405),
     "POST /upload HTTP/1.1\r\nHost: localhost\r\nContent-Length: 4\r\n\r\ndata"),

    # HEAD → non supporté → 405
    ("METHOD_HEAD_NOT_SUPPORTED",
     405,
     "HEAD / HTTP/1.1\r\nHost: localhost\r\n\r\n"),

    # PUT → non supporté → 405
    ("METHOD_PUT_NOT_SUPPORTED",
     405,
     "PUT / HTTP/1.1\r\nHost: localhost\r\nContent-Length: 4\r\n\r\ndata"),

    # OPTIONS → non supporté → 405
    ("METHOD_OPTIONS_NOT_SUPPORTED",
     405,
     "OPTIONS / HTTP/1.1\r\nHost: localhost\r\n\r\n"),

    # PATCH → non supporté → 405
    ("METHOD_PATCH_NOT_SUPPORTED",
     405,
     "PATCH / HTTP/1.1\r\nHost: localhost\r\n\r\n"),

    # Méthode inconnue → 405
    ("INVALID_METHOD_UNKNOWN",
     405,
     "HELLO / HTTP/1.1\r\nHost: localhost\r\n\r\n"),

    # Méthode en minuscules → 400
    ("INVALID_METHOD_LOWERCASE",
     400,
     "get / HTTP/1.1\r\nHost: localhost\r\n\r\n"),

    # Méthode mixte → 400
    ("INVALID_METHOD_MIXEDCASE",
     400,
     "Get / HTTP/1.1\r\nHost: localhost\r\n\r\n"),

    # ──────────────────────────────────────────────────────
    # HEADERS
    # ──────────────────────────────────────────────────────

    # Host manquant → 400
    ("MISSING_HOST",
     400,
     "GET / HTTP/1.1\r\n\r\n"),

    # Header sans deux-points → 400
    ("BROKEN_HEADER_NO_COLON",
     400,
     "GET / HTTP/1.1\r\nHost localhost\r\n\r\n"),

    # Host dupliqué → 400
    ("DOUBLE_HOST",
     400,
     "GET / HTTP/1.1\r\nHost: localhost\r\nHost: localhost\r\n\r\n"),

    # Header sans valeur → 400
    ("HEADER_NO_VALUE",
     400,
     "GET / HTTP/1.1\r\nHost:\r\n\r\n"),

    # Header valeur espaces seulement → 400
    ("HEADER_ONLY_SPACES",
     400,
     "GET / HTTP/1.1\r\nHost:    \r\n\r\n"),

    # CR dans valeur header → 400
    ("HEADER_CR_IN_VALUE",
     400,
     "GET / HTTP/1.1\r\nHost: local\rhost\r\n\r\n"),

    # Null byte dans valeur → 400
    ("HEADER_NULL_BYTE_IN_VALUE",
     400,
     "GET / HTTP/1.1\r\nHost: local\x00host\r\n\r\n"),

    # Header folding obsolète → 400
    ("HEADER_FOLDING_OBSOLETE",
     400,
     "GET / HTTP/1.1\r\nHost: localhost\r\nX-Folded: value\r\n  continuation\r\n\r\n"),

    # Trop de headers → 431
    ("TOO_MANY_HEADERS",
     431,
     "GET / HTTP/1.1\r\nHost: localhost\r\n"
     + "".join(f"X-Header-{i}: value\r\n" for i in range(200)) + "\r\n"),

    # Nom de header très long → 400
    ("VERY_LONG_HEADER_NAME",
     400,
     "GET / HTTP/1.1\r\nHost: localhost\r\n" + "X-" + "A" * 8000 + ": value\r\n\r\n"),

    # Valeur de header très longue → 400
    ("VERY_LONG_HEADER_VALUE",
     400,
     "GET / HTTP/1.1\r\nHost: localhost\r\nX-Custom: " + "A" * 8000 + "\r\n\r\n"),

    # Host avec port → valide
    ("HOST_WITH_PORT",
     200,
     "GET / HTTP/1.1\r\nHost: localhost:8080\r\n\r\n"),

    # Host en IP → valide
    ("HOST_AS_IP",
     200,
     "GET / HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n"),

    # ──────────────────────────────────────────────────────
    # BODY
    # ──────────────────────────────────────────────────────

    # Body > client_max_body_size (1MB) → 413
    ("BODY_TOO_BIG",
     413,
     "POST /contacts HTTP/1.1\r\nHost: localhost\r\nContent-Length: 2000000\r\n\r\n" + "A" * 2000000),

    # Body sur rshin > 0 (client_max_body_size 0) → 413
    ("BODY_BLOCKED_ON_RSHIN",
     413,
     "POST / HTTP/1.1\r\nHost: rshin\r\nContent-Length: 5\r\n\r\nhello"),

    # Content-Length déclaré mais body trop court → 400
    ("BODY_SHORTER_THAN_CL",
     400,
     "POST /contacts HTTP/1.1\r\nHost: localhost\r\nContent-Length: 100\r\n\r\nhello"),

    # Double Content-Length → 400
    ("DOUBLE_CONTENT_LENGTH",
     400,
     "POST /contacts HTTP/1.1\r\nHost: localhost\r\nContent-Length: 5\r\nContent-Length: 10\r\n\r\nhello"),

    # Content-Length négatif → 400
    ("NEGATIVE_CONTENT_LENGTH",
     400,
     "POST /contacts HTTP/1.1\r\nHost: localhost\r\nContent-Length: -1\r\n\r\nhello"),

    # Content-Length non numérique → 400
    ("CONTENT_LENGTH_STRING",
     400,
     "POST /contacts HTTP/1.1\r\nHost: localhost\r\nContent-Length: abc\r\n\r\nhello"),

    # Content-Length flottant → 400
    ("CONTENT_LENGTH_FLOAT",
     400,
     "POST /contacts HTTP/1.1\r\nHost: localhost\r\nContent-Length: 3.5\r\n\r\nhello"),

    # POST sans Content-Length → 400
    ("POST_WITHOUT_CONTENT_LENGTH",
     400,
     "POST /contacts HTTP/1.1\r\nHost: localhost\r\n\r\nhello"),

    # GET avec body → 400
    ("GET_WITH_BODY",
     400,
     "GET / HTTP/1.1\r\nHost: localhost\r\nContent-Length: 5\r\n\r\nhello"),

    # Chunked valide sur /contacts → 200 ou 201
    ("CHUNKED_VALID",
     (200, 201),
     "POST /contacts HTTP/1.1\r\nHost: localhost\r\nTransfer-Encoding: chunked\r\n\r\n5\r\nhello\r\n0\r\n\r\n"),

    # Chunked + Content-Length → 400
    ("CHUNKED_AND_CONTENT_LENGTH",
     400,
     "POST /contacts HTTP/1.1\r\nHost: localhost\r\nTransfer-Encoding: chunked\r\nContent-Length: 5\r\n\r\n5\r\nhello\r\n0\r\n\r\n"),

    # ──────────────────────────────────────────────────────
    # URI
    # ──────────────────────────────────────────────────────

    # URI trop longue → 414
    ("LONG_URI",
     414,
     "GET /" + "A" * 8000 + " HTTP/1.1\r\nHost: localhost\r\n\r\n"),

    # URI vide → 400
    ("EMPTY_URI",
     400,
     "GET  HTTP/1.1\r\nHost: localhost\r\n\r\n"),

    # Fragment dans l'URI → 400
    ("URI_WITH_FRAGMENT",
     400,
     "GET /page#section HTTP/1.1\r\nHost: localhost\r\n\r\n"),

    # Path traversal → 400
    ("URI_PATH_TRAVERSAL",
     400,
     "GET /../../../etc/passwd HTTP/1.1\r\nHost: localhost\r\n\r\n"),

    # Double slash → 400
    ("URI_DOUBLE_SLASH",
     400,
     "GET //etc/passwd HTTP/1.1\r\nHost: localhost\r\n\r\n"),

    # Null byte dans l'URI → 400
    ("URI_NULL_BYTE",
     400,
     "GET /path\x00/hidden HTTP/1.1\r\nHost: localhost\r\n\r\n"),

    # Espace non encodé → 400
    ("URI_SPACE_UNENCODED",
     400,
     "GET /path with spaces HTTP/1.1\r\nHost: localhost\r\n\r\n"),

    # % incomplet → 400
    ("URI_PERCENT_INCOMPLETE",
     400,
     "GET /path%2 HTTP/1.1\r\nHost: localhost\r\n\r\n"),

    # ──────────────────────────────────────────────────────
    # PROTOCOL
    # ──────────────────────────────────────────────────────

    # Version inconnue → 505
    ("BAD_HTTP_VERSION",
     505,
     "GET / HTTP/9.9\r\nHost: localhost\r\n\r\n"),

    # HTTP/2.0 → 505
    ("HTTP_2_0_NOT_SUPPORTED",
     505,
     "GET / HTTP/2.0\r\nHost: localhost\r\n\r\n"),

    # HTTP/1.0 → accepté ou 505 selon implémentation
    ("HTTP_1_0",
     (200, 505),
     "GET / HTTP/1.0\r\nHost: localhost\r\n\r\n"),

    # Version en minuscules → 400
    ("LOWERCASE_HTTP_VERSION",
     400,
     "GET / http/1.1\r\nHost: localhost\r\n\r\n"),

    # Pas de version → 400
    ("NO_HTTP_VERSION",
     400,
     "GET /\r\nHost: localhost\r\n\r\n"),

    # ──────────────────────────────────────────────────────
    # REQUEST LINE FORMAT
    # ──────────────────────────────────────────────────────

    # Requête vide → 400
    ("EMPTY_REQUEST",
     400,
     "\r\n"),

    # Request line manquante → 400
    ("MISSING_REQUEST_LINE",
     400,
     "\r\nHost: localhost\r\n\r\n"),

    # Espaces supplémentaires → 400
    ("EXTRA_SPACE_IN_REQUEST_LINE",
     400,
     "GET  /  HTTP/1.1\r\nHost: localhost\r\n\r\n"),

    # LF seul sans CR → 400
    ("REQUEST_LINE_ONLY_LF",
     400,
     "GET / HTTP/1.1\nHost: localhost\n\n"),

    # CR sans LF → 400
    ("CR_WITHOUT_LF",
     400,
     "GET / HTTP/1.1\rHost: localhost\r\r"),

    # ──────────────────────────────────────────────────────
    # FICHIERS STATIQUES
    # ──────────────────────────────────────────────────────

    # Fichier inexistant → 404 avec page d'erreur
    ("STATIC_NOT_FOUND",
     404,
     "GET /this_does_not_exist.html HTTP/1.1\r\nHost: localhost\r\n\r\n"),

    # Index par défaut → 200
    ("STATIC_INDEX",
     200,
     "GET / HTTP/1.1\r\nHost: localhost\r\n\r\n"),

    # ──────────────────────────────────────────────────────
    # PAGES D'ERREUR (body non vide obligatoire)
    # ──────────────────────────────────────────────────────

    ("DEFAULT_ERROR_PAGE_404",
     404,
     "GET /nonexistent HTTP/1.1\r\nHost: localhost\r\n\r\n"),

    ("DEFAULT_ERROR_PAGE_405",
     405,
     "HEAD / HTTP/1.1\r\nHost: localhost\r\n\r\n"),

    # ──────────────────────────────────────────────────────
    # SÉCURITÉ
    # ──────────────────────────────────────────────────────

    ("HEADER_INJECTION_CRLF",
     400,
     "GET / HTTP/1.1\r\nHost: localhost\r\nX-Injected: evil\r\n\r\n"),
]

# ─────────────────────────────────────────────
# Sections
# ─────────────────────────────────────────────
SECTION_PREFIXES = {
    "VALID":                "VALID REQUESTS",
    "METHOD":               "MÉTHODES",
    "INVALID_METHOD":       "MÉTHODES",
    "MISSING_HOST":         "HEADERS",
    "BROKEN":               "HEADERS",
    "DOUBLE_HOST":          "HEADERS",
    "HEADER":               "HEADERS",
    "TOO":                  "HEADERS",
    "VERY_LONG_HEADER":     "HEADERS",
    "HOST":                 "HEADERS",
    "BODY":                 "BODY",
    "POST_WITHOUT":         "BODY",
    "GET_WITH":             "BODY",
    "DOUBLE_CONTENT":       "BODY",
    "NEGATIVE":             "BODY",
    "CONTENT":              "BODY",
    "CHUNKED":              "BODY",
    "LONG_URI":             "URI",
    "EMPTY_URI":            "URI",
    "URI":                  "URI",
    "BAD_HTTP":             "PROTOCOL",
    "HTTP":                 "PROTOCOL",
    "LOWERCASE_HTTP":       "PROTOCOL",
    "NO_HTTP":              "PROTOCOL",
    "EMPTY_REQUEST":        "REQUEST LINE FORMAT",
    "MISSING_REQUEST":      "REQUEST LINE FORMAT",
    "EXTRA":                "REQUEST LINE FORMAT",
    "REQUEST":              "REQUEST LINE FORMAT",
    "CR":                   "REQUEST LINE FORMAT",
    "STATIC":               "FICHIERS STATIQUES",
    "DEFAULT_ERROR":        "PAGES D'ERREUR",
    "SMUGGLE":              "HTTP SMUGGLING",
    "PIPELINE":             "PIPELINING",
    "SLOW":                 "SLOWLORIS",
    "UNICODE":              "UNICODE / ENCODING",
}

def get_section(name):
    for prefix, section in sorted(SECTION_PREFIXES.items(), key=lambda x: -len(x[0])):
        if name.startswith(prefix):
            return section
    return "OTHER"

# ─────────────────────────────────────────────
# ANSI
# ─────────────────────────────────────────────
GREEN   = "\033[32m"
RED     = "\033[31m"
YELLOW  = "\033[33m"
CYAN    = "\033[36m"
MAGENTA = "\033[35m"
RESET   = "\033[0m"
BOLD    = "\033[1m"
DIM     = "\033[2m"

passed = 0
failed = 0
errors = 0

def _fmt(expected):
    if isinstance(expected, tuple):
        return "|".join(str(c) for c in expected)
    return str(expected)

def _matches(got, expected):
    if isinstance(expected, tuple):
        return got in expected
    return got == expected

def _pass(name, detail):
    global passed; passed += 1
    print(f"  [{GREEN}PASS{RESET}]  {name:<45} {detail}")

def _fail(name, detail):
    global failed; failed += 1
    print(f"  [{RED}FAIL{RESET}]  {name:<45} {detail}")

def _err(name, expected, detail):
    global errors; errors += 1
    print(f"  [{YELLOW}ERR {RESET}]  {name:<45} {YELLOW}{detail}{RESET}  {DIM}(expected {_fmt(expected)}){RESET}")

def _print_result(name, expected, got_code, got_str, duration):
    exp_label = f"{DIM}expected {BOLD}{_fmt(expected)}{RESET}"
    if _matches(got_code, expected):
        _pass(name, f"{got_str}  {DIM}({duration:.1f} ms){RESET}")
    else:
        _fail(name, f"got [{RED}{got_str}{RESET}]  {exp_label}  ({duration:.1f} ms)")

def send_test(name, expected, request):
    try:
        s = socket.socket()
        s.settimeout(5)
        start = time.time()
        s.connect((HOST, PORT))
        s.send(request.encode(errors="surrogateescape"))
        response = s.recv(4096)
        duration = (time.time() - start) * 1000
        s.close()

        if not response:
            _print_result(name, expected, None, "NO RESPONSE", duration)
            return

        first_line = response.decode(errors="ignore").split("\r\n")[0]
        parts      = first_line.split(" ", 2)
        got_code   = int(parts[1]) if len(parts) >= 2 and parts[1].isdigit() else None

        # Pages d'erreur : vérifier que le body n'est pas vide
        if name.startswith("DEFAULT_ERROR") and _matches(got_code, expected):
            body = response.decode(errors="ignore")
            content = body.split("\r\n\r\n", 1)[1].strip() if "\r\n\r\n" in body else ""
            if content:
                _pass(name, f"{first_line} + body présent  {DIM}({duration:.1f} ms){RESET}")
            else:
                _fail(name, f"got [{first_line}] mais body vide — page d'erreur manquante  ({duration:.1f} ms)")
            return

        _print_result(name, expected, got_code, first_line, duration)

    except Exception as e:
        err_str = str(e)
        if expected == "TIMEOUT" and "timed out" in err_str:
            _pass(name, "timed out as expected")
        else:
            _err(name, expected, err_str)

# ─────────────────────────────────────────────
# COMPLEX TESTS
# ─────────────────────────────────────────────

def test_smuggle_cl_te():
    """TE + CL ensemble → 400"""
    name, expected = "SMUGGLE_CL_TE", 400
    payload = (
        "POST /contacts HTTP/1.1\r\nHost: localhost\r\n"
        "Content-Length: 11\r\nTransfer-Encoding: chunked\r\n\r\n"
        "0\r\n\r\nG"
    )
    try:
        s = socket.socket(); s.settimeout(3); start = time.time()
        s.connect((HOST, PORT)); s.send(payload.encode())
        resp = b""
        while True:
            chunk = s.recv(4096)
            if not chunk: break
            resp += chunk
        duration = (time.time() - start) * 1000; s.close()
        fl = resp.decode(errors="ignore").split("\r\n")[0]
        p  = fl.split(" ", 2)
        _print_result(name, expected, int(p[1]) if len(p)>=2 and p[1].isdigit() else None, fl, duration)
    except Exception as e: _err(name, expected, str(e))

def test_smuggle_te_obfuscated():
    """TE obfusqué (xchunked) → 400"""
    name, expected = "SMUGGLE_TE_OBFUSCATED", 400
    payload = (
        "POST /contacts HTTP/1.1\r\nHost: localhost\r\n"
        "Transfer-Encoding: xchunked\r\nContent-Length: 5\r\n\r\nhello"
    )
    try:
        s = socket.socket(); s.settimeout(3); start = time.time()
        s.connect((HOST, PORT)); s.send(payload.encode())
        resp = s.recv(4096); duration = (time.time() - start) * 1000; s.close()
        fl = resp.decode(errors="ignore").split("\r\n")[0]
        p  = fl.split(" ", 2)
        _print_result(name, expected, int(p[1]) if len(p)>=2 and p[1].isdigit() else None, fl, duration)
    except Exception as e: _err(name, expected, str(e))

def test_smuggle_chunk_overflow():
    """Chunk size overflow → 400"""
    name, expected = "SMUGGLE_CHUNK_OVERFLOW", 400
    payload = (
        "POST /contacts HTTP/1.1\r\nHost: localhost\r\n"
        "Transfer-Encoding: chunked\r\n\r\n"
        "FFFFFFFFFFFFFFFF\r\nhello\r\n0\r\n\r\n"
    )
    try:
        s = socket.socket(); s.settimeout(3); start = time.time()
        s.connect((HOST, PORT)); s.send(payload.encode())
        resp = s.recv(4096); duration = (time.time() - start) * 1000; s.close()
        fl = resp.decode(errors="ignore").split("\r\n")[0]
        p  = fl.split(" ", 2)
        _print_result(name, expected, int(p[1]) if len(p)>=2 and p[1].isdigit() else None, fl, duration)
    except Exception as e: _err(name, expected, str(e))

def test_pipeline_two_gets():
    """Pipelining : 2 GET dans un seul write → 2 × 200"""
    name, expected = "PIPELINE_TWO_GETS", 200
    payload = (
        "GET / HTTP/1.1\r\nHost: localhost\r\n\r\n"
        "GET / HTTP/1.1\r\nHost: localhost\r\n\r\n"
    )
    try:
        s = socket.socket(); s.settimeout(3); start = time.time()
        s.connect((HOST, PORT)); s.send(payload.encode())
        resp = b""
        while True:
            try:
                chunk = s.recv(4096)
                if not chunk: break
                resp += chunk
            except socket.timeout: break
        duration = (time.time() - start) * 1000; s.close()
        responses = [l for l in resp.decode(errors="ignore").split("\r\n") if l.startswith("HTTP/")]
        count_200 = sum(1 for r in responses if "200" in r)
        if count_200 >= 2:
            _pass(name, f"got {count_200}× 200 OK  ({duration:.1f} ms)")
        else:
            _fail(name, f"got {responses}  expected 2× 200 OK  ({duration:.1f} ms)")
    except Exception as e: _err(name, expected, str(e))

def test_pipeline_post_then_get():
    """Pipelining : POST /contacts + GET / → 2 réponses"""
    name, expected = "PIPELINE_POST_THEN_GET", (200, 201)
    payload = (
        "POST /contacts HTTP/1.1\r\nHost: localhost\r\nContent-Length: 5\r\n\r\nhello"
        "GET / HTTP/1.1\r\nHost: localhost\r\n\r\n"
    )
    try:
        s = socket.socket(); s.settimeout(3); start = time.time()
        s.connect((HOST, PORT)); s.send(payload.encode())
        resp = b""
        while True:
            try:
                chunk = s.recv(4096)
                if not chunk: break
                resp += chunk
            except socket.timeout: break
        duration = (time.time() - start) * 1000; s.close()
        responses = [l for l in resp.decode(errors="ignore").split("\r\n") if l.startswith("HTTP/")]
        if len(responses) >= 2:
            _pass(name, f"got {len(responses)} réponses  ({duration:.1f} ms)")
        else:
            _fail(name, f"got seulement {len(responses)} réponse(s): {responses}  ({duration:.1f} ms)")
    except Exception as e: _err(name, expected, str(e))

def test_slow_body():
    """Slow body — sujet: 'never hang indefinitely' → 408"""
    name, expected = "SLOW_BODY_INCOMPLETE", 408
    headers = "POST /contacts HTTP/1.1\r\nHost: localhost\r\nContent-Length: 100\r\n\r\n"
    try:
        s = socket.socket(); s.settimeout(10); start = time.time()
        s.connect((HOST, PORT))
        s.send(headers.encode())
        s.send(b"A" * 10)
        time.sleep(4)
        resp = s.recv(4096); duration = (time.time() - start) * 1000; s.close()
        fl = resp.decode(errors="ignore").split("\r\n")[0]
        p  = fl.split(" ", 2)
        got = int(p[1]) if len(p)>=2 and p[1].isdigit() else None
        if got == 408:
            _pass(name, f"{fl}  ({duration:.1f} ms)")
        else:
            _fail(name, f"got [{fl}]  {DIM}expected {BOLD}408{RESET}  ({duration:.1f} ms)")
    except socket.timeout:
        _fail(name, "server never responded — VULNERABLE au slow-body DoS")
    except Exception as e: _err(name, expected, str(e))

def test_slow_many_connections():
    """50 conns half-open + 1 légitime — sujet: 'remains available at all times'"""
    name, expected = "SLOW_CONNECTION_EXHAUSTION", 200
    N = 50
    sockets = []
    incomplete = "GET / HTTP/1.1\r\nHost: localhost\r\nX-Padding: " + "A" * 100
    for _ in range(N):
        try:
            s = socket.socket(); s.settimeout(2)
            s.connect((HOST, PORT)); s.send(incomplete.encode())
            sockets.append(s)
        except Exception: break
    try:
        s = socket.socket(); s.settimeout(3); start = time.time()
        s.connect((HOST, PORT))
        s.send(b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n")
        resp = s.recv(4096); duration = (time.time() - start) * 1000; s.close()
        fl = resp.decode(errors="ignore").split("\r\n")[0]
        p  = fl.split(" ", 2)
        got = int(p[1]) if len(p)>=2 and p[1].isdigit() else None
        _print_result(name, expected, got, f"{fl} (après {len(sockets)} conns lentes)", duration)
    except Exception as e: _err(name, expected, str(e))
    finally:
        for s in sockets:
            try: s.close()
            except Exception: pass

def test_unicode_traversal():
    """Double percent-encoding '../' → 400 ou 404"""
    name, expected = "UNICODE_DOUBLE_PERCENT_TRAVERSAL", (400, 404)
    payload = b"GET /%252e%252e%252fetc%252fpasswd HTTP/1.1\r\nHost: localhost\r\n\r\n"
    try:
        s = socket.socket(); s.settimeout(3); start = time.time()
        s.connect((HOST, PORT)); s.send(payload)
        resp = s.recv(4096); duration = (time.time() - start) * 1000; s.close()
        fl = resp.decode(errors="ignore").split("\r\n")[0]
        p  = fl.split(" ", 2)
        got = int(p[1]) if len(p)>=2 and p[1].isdigit() else None
        _print_result(name, expected, got, fl, duration)
    except Exception as e: _err(name, expected, str(e))

def test_unicode_overlong_slash():
    """Overlong UTF-8 de '/' → 400"""
    name, expected = "UNICODE_OVERLONG_SLASH", 400
    payload = b"GET /\xc0\xafetc\xc0\xafpasswd HTTP/1.1\r\nHost: localhost\r\n\r\n"
    try:
        s = socket.socket(); s.settimeout(3); start = time.time()
        s.connect((HOST, PORT)); s.send(payload)
        resp = s.recv(4096); duration = (time.time() - start) * 1000; s.close()
        fl = resp.decode(errors="ignore").split("\r\n")[0]
        p  = fl.split(" ", 2)
        got = int(p[1]) if len(p)>=2 and p[1].isdigit() else None
        _print_result(name, expected, got, fl, duration)
    except Exception as e: _err(name, expected, str(e))

# ─────────────────────────────────────────────
# RUNNER
# ─────────────────────────────────────────────

print(f"\n{BOLD}{'='*66}{RESET}")
print(f"{BOLD}  WEBSERV 42 — HTTP TESTER  —  {HOST}:{PORT}{RESET}")
print(f"{BOLD}  Config : tester.conf{RESET}")
print(f"{BOLD}  Vhost localhost → /  /contacts{RESET}")
print(f"{BOLD}  Vhost rshin     → /upload  /delete{RESET}")
print(f"{BOLD}  expected X|Y = plusieurs codes acceptés{RESET}")
print(f"{BOLD}{'='*66}{RESET}")

current_section = None
for name, expected, request in tests:
    section = get_section(name)
    if section != current_section:
        current_section = section
        print(f"\n  {CYAN}{BOLD}── {section} ──{RESET}")
    send_test(name, expected, request)

complex_tests = [
    ("HTTP SMUGGLING",     [test_smuggle_cl_te, test_smuggle_te_obfuscated, test_smuggle_chunk_overflow]),
    ("PIPELINING",         [test_pipeline_two_gets, test_pipeline_post_then_get]),
    ("SLOWLORIS / DoS",    [test_slow_body, test_slow_many_connections]),
    ("UNICODE / ENCODING", [test_unicode_traversal, test_unicode_overlong_slash]),
]

for section_name, fns in complex_tests:
    print(f"\n  {MAGENTA}{BOLD}── {section_name} (COMPLEX) ──{RESET}")
    for fn in fns:
        fn()

total  = passed + failed + errors
bar_w  = 30
p_fill = int(bar_w * passed / total) if total else 0
f_fill = int(bar_w * failed / total) if total else 0
e_fill = bar_w - p_fill - f_fill
bar    = f"{GREEN}{'█'*p_fill}{RED}{'█'*f_fill}{YELLOW}{'█'*e_fill}{RESET}"

print(f"\n{BOLD}{'='*66}{RESET}")
print(f"  {bar}  {BOLD}{GREEN}{passed} passed{RESET} / {RED}{failed} failed{RESET} / {YELLOW}{errors} errors{RESET} / {total} total")
print(f"{BOLD}{'='*66}{RESET}\n")
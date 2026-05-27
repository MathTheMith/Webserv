*This project has been created as part of the 42 curriculum by nofanizz, mvachon, lmarcucc*

# webserv

## Description

This project was developed as part of the 42 curriculum.
Its goal is to build a functional HTTP/1.1 web server in C++98, inspired by nginx, capable of serving static files, handling dynamic content via CGI, and managing multiple virtual hosts simultaneously.

The project focuses on:
- Parsing and validating a structured configuration file (nginx-like syntax)
- Implementing the HTTP/1.1 protocol from scratch (request parsing, response building, status codes, headers)
- Using a single non-blocking `poll()` call to handle all I/O — client connections, CGI pipes, and file operations — without threads or forking the main process

### Overview

The server is designed to:
- Read a `.conf` file at startup, validate every directive, and build an internal representation of each virtual server and its locations
- Bind one listening socket per unique `host:port` pair and group multiple virtual servers behind it (selection is done via the `Host` header)
- Accept client connections and process their requests through a state machine: read → parse → route → respond
- Serve static files from a configurable document root, with support for custom index files and automatic directory listings (autoindex)
- Execute CGI scripts (e.g. Python 3) by forking a child process, piping the request body to its stdin, and streaming its stdout back as the HTTP response
- Handle file uploads by writing request bodies to a configurable upload directory
- Return custom error pages for any 4xx/5xx status code

This project helped us improve our understanding of:
- The HTTP/1.1 protocol (request/response cycle, headers, status codes, chunked encoding)
- Low-level socket programming (`socket`, `bind`, `listen`, `accept`, `recv`, `send`)
- Non-blocking I/O and event-driven architecture with `poll()`
- Process management for CGI (`fork`, `execve`, `pipe`, `waitpid`)
- Team collaboration, modular C++ design, and project organization

The idea behind it is to reproduce core nginx behavior in order to launch proper web servers.

---

# Instructions

## Requirements

- GCC / Clang
- Make
- Linux / macOS

## Compilation

Clone the repository and compile the project using:

```bash
git clone git@github.com:NoaFanizzi/webserv.git
cd webserv
make
```

## Config file

- See `config.conf` for a working example, and `config_format.md` for the full directive reference
- The file must have a `.conf` extension

## Executable

```bash
./webserv yourconfigfile.conf
```

Stop the server at any time with `Ctrl+C` (clean shutdown).

---

# Ressources

## Useful links
HTTP protocol
- https://developer.mozilla.org/fr/docs/Web/HTTP/Guides/Overview

Response Status
- https://developer.mozilla.org/fr/docs/Web/HTTP/Reference/Status

Configuration file
- https://nginx.org/en/docs/http/configuring_https_servers.html

CGI (common Gateway Interface)
- https://en.wikipedia.org/wiki/Common_Gateway_Interface

## A.I.

AI was mainly used to dig deeper into some technical concepts such as poll, and why it was pertinent in our project. In the same ways, it gave us some interesting insights about the way to improve our code and his architecture (nevertheless, it wasn't always pertinent regarding our perception of the project). Finally, It eventually helped us to spot some edge cases which are very important to ensure a propre behavior of our project.

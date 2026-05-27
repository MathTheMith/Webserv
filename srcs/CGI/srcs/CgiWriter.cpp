/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   CgiWriter.cpp                                      :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: nofanizz <nofanizz@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/05/27 13:55:10 by nofanizz          #+#    #+#             */
/*   Updated: 2026/05/27 13:59:24 by nofanizz         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "CgiWriter.hpp"
#include "WebServer.hpp"
#include <poll.h>
#include <fcntl.h>

CgiWriter::CgiWriter(const int fd, const std::string body) : _timedOut(false), _body(body), _written(0)
{
	_fd = fd;
	_fullSize = body.size();
	_closedStatus = false;
	_events = POLLOUT;
	_startTime = std::time(NULL);
	WebServer::pollFdCreation(_fd, this);
}

void CgiWriter::pollOutHandler() {

	if (_timedOut)
		return ;
	ssize_t toSend;
	if (_fullSize - _written > WRITEBUFFSIZE)
		toSend = WRITEBUFFSIZE;
	else
		toSend = _fullSize - _written;

	const char *to_write = _body.data() + _written;
	ssize_t bytesWriten = write(_fd, to_write, toSend);
	if (bytesWriten == -1) {
		_events = 0;
		_closedStatus = true;
		return ;
	}
	_written += bytesWriten;
	if (_written == _fullSize) {
		_events = 0;
		_closedStatus = true;
	}
}

void CgiWriter::onTimeout() {
	_closedStatus = true;
	_events = 0;
}

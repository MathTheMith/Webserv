/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   CgiWriter.hpp                                      :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: nofanizz <nofanizz@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/05/27 12:43:59 by nofanizz          #+#    #+#             */
/*   Updated: 2026/05/27 13:54:46 by nofanizz         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef CGI_WRITER_HPP
#define CGI_WRITER_HPP

#include "AManager.hpp"
#include <string>

#ifndef WRITEBUFFSIZE
#define WRITEBUFFSIZE 2
#endif

class CgiWriter : public AManager
{
private:
	bool _timedOut;
	const std::string _body;
	ssize_t _fullSize;
	ssize_t _written;
public:
	CgiWriter(const int _fd, const std::string body);
	~CgiWriter() {};

	void pollInHandler() {}
	void pollOutHandler();

	void onTimeout();
};

#endif

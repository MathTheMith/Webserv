/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   CgiManager.hpp                                     :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: nofanizz <nofanizz@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/05/27 14:09:52 by nofanizz          #+#    #+#             */
/*   Updated: 2026/05/27 14:09:55 by nofanizz         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef CGIMANAGER_HPP
#define CGIMANAGER_HPP

#include "Request.hpp"
#include "AManager.hpp"
#include <string>
#include <vector>

#include "Client.hpp"

class CgiManager
{
private:
	// variables
	std::vector<std::string> _env;
	const Request &_request;
	std::string &_scriptPath;
	std::string &_interpreter;
	Client &_client;

	int _fdIn[2];
	int _fdOut[2];
	pid_t _pid;

	// functions
	void buildEnv();
	char **envToCharArray() const;

public:
	// constructor
	CgiManager(Client &client, std::string &scriptPath, std::string &interpreter);
	~CgiManager() {}

	static std::string getCgiInterpreter(const std::string &path, const Request &req);

	bool start();
};

#endif

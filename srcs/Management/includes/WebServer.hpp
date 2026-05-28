/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   WebServer.hpp                                      :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: nofanizz <nofanizz@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/05/28 14:56:26 by nofanizz          #+#    #+#             */
/*   Updated: 2026/05/28 14:56:36 by nofanizz         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef WEBSERVER_H
#define WEBSERVER_H

#include <map>
#include <ctime>
#include <vector>

class AManager;

class WebServer
{
	private:
		// variables
		static std::vector <struct pollfd> _pollfds;
		static std::map <int, AManager *> _managers;
		static void updateStatus();
		static AManager* getManager(int fd);
		static bool _finalAutoIndex;
		static bool _firstLoopRequest;
		static bool _requestEnded;
		
	public:
		//functions
		static void pollFdCreation(const int &fd, AManager *manager);
		static void	run();
		static void destroy();

};

#endif

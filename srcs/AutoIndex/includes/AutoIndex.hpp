/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   AutoIndex.hpp                                      :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: nofanizz <nofanizz@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/02/05 15:35:57 by nofanizz          #+#    #+#             */
/*   Updated: 2026/05/27 13:53:15 by nofanizz         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef AUTOINDEX_HPP
#define AUTOINDEX_HPP

#include <string>

class AutoIndex
{
	private:
		static std::string _header;
		static std::string _template;
		std::string _content;
		static std::string _footer;
		const std::string _root;
		const std::string _location;
	public:

		//basics
		AutoIndex(const std::string &root, const std::string &location);
		
		//methods
		std::string initAutoIndex(const std::string &rPath);
		std::string replaceTemplate(struct dirent &sdir, const std::string &rPath);
		void addNewRow(struct dirent &sdir, const std::string &rPath);
		void replaceName(std::string &newTemplate, struct dirent &sdir);
		void replaceLink(std::string &newTemplate, struct dirent &sdir);
		void replaceDate(std::string &newTemplate, struct stat &file);
		void replaceWeight(std::string &newTemplate, struct stat &file);

};

#endif

# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    cgi.mk                                             :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: nofanizz <nofanizz@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/01/31 11:14:01 by nofanizz          #+#    #+#              #
#    Updated: 2026/05/28 15:54:16 by nofanizz         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

SRCS += srcs/CGI/srcs/CgiManager.cpp \
		srcs/CGI/srcs/CgiWriter.cpp \
		srcs/CGI/srcs/CgiReader.cpp

INCLUDES += -Isrcs/CGI/includes

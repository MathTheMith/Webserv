# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    configparser.mk                                    :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: nofanizz <nofanizz@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/01/31 11:14:27 by nofanizz          #+#    #+#              #
#    Updated: 2026/05/28 14:52:52 by nofanizz         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

SRCS += srcs/ConfigParser/srcs/Config.cpp \
        srcs/ConfigParser/srcs/ConfigParser.cpp \
        srcs/ConfigParser/srcs/LocationParser.cpp \
        srcs/ConfigParser/srcs/ServerDirectives.cpp \
        srcs/ConfigParser/srcs/ServerParser.cpp

INCLUDES += -Isrcs/ConfigParser/includes

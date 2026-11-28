# SPDX-License-Identifier: BSD-2-Clause
ifndef PS5_PAYLOAD_SDK
$(error Set PS5_PAYLOAD_SDK to the extracted PS5 Payload SDK directory)
endif
CC := $(PS5_PAYLOAD_SDK)/bin/prospero-clang
CFLAGS := -Os -Wall -Wextra -Werror -fno-ident -ffile-prefix-map="$(CURDIR)"=.
LDFLAGS := -Wl,--build-id=none
LDLIBS := -lSceUserService

.PHONY: all
all: build/return-home-uri.elf

build/return-home-uri.elf: src/main.c Makefile
	mkdir -p build
	"$(CC)" $(CFLAGS) $(LDFLAGS) -o $@ $< $(LDLIBS)

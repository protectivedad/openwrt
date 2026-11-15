# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2013-2021 OpenWrt.org

include $(TOPDIR)/rules.mk

PKG_NAME:=dsp-w115
PKG_RELEASE:=1

PKG_BUILD_DIR := $(BUILD_DIR)/$(PKG_NAME)

include $(INCLUDE_DIR)/package.mk

define Package/dps-w115
  SECTION:=utils
  CATEGORY:=Base system
  DEPENDS:= \
	+@BUSYBOX_CONFIG_UDHCPD \
	+@BUSYBOX_CONFIG_INOTIFYD \
	+kmod-gpio-button-hotplug \
	+micropython-mbedtls \
	+zram-swap
  TITLE:=DSP-W115 Utils
  PKGARCH:=all
endef

define Package/dps-w115/description
 A set of scripts and configurations that allow D-Link DSP-W115 smart
 plug to connect to a MQTTS broker for control and publishing data.
endef

define Package/dps-w115/conffiles
/etc/config/mqtt-client
/etc/ca.der
/etc/ca.crt
endef

define Build/Prepare
endef

define Build/Configure
endef

define Build/Compile
endef

define Package/dps-w115/install
	$(INSTALL_DIR) $(1)/etc/init.d
	$(INSTALL_BIN) ./files/udhcpd.init $(1)/etc/init.d/udhcpd
	$(INSTALL_BIN) ./files/relay_led.init $(1)/etc/init.d/relay_led
	$(INSTALL_DIR) $(1)/etc/rc.button
	$(INSTALL_BIN) ./files/brightness_zero $(1)/etc/rc.button/brightness_zero
	$(INSTALL_BIN) ./files/lights_toggle $(1)/etc/rc.button/lights_toggle
	$(INSTALL_DIR) $(1)/usr/bin
	$(INSTALL_BIN) ./files/brightness_control.sh $(1)/usr/bin/brightness_control.sh
	$(INSTALL_BIN) ./files/relay_control.sh $(1)/usr/bin/relay_control.sh
	$(INSTALL_BIN) ./files/led_control.sh $(1)/usr/bin/led_control.sh
	$(INSTALL_BIN) ./files/mqtt-client.py $(1)/usr/bin/mqtt-client.py
	$(INSTALL_BIN) ./files/mqtt-client.mpy $(1)/usr/bin/mqtt-client.mpy
	$(INSTALL_DIR) $(1)/etc/hotplug.d/iface
	$(INSTALL_BIN) ./files/99-mqtt-client.hotplug $(1)/etc/hotplug.d/iface/99-mqtt-client
	$(INSTALL_DIR) $(1)/etc/uci-defaults
	$(INSTALL_BIN) ./files/50_mqtt-client.uci-defaults $(1)/etc/uci-defaults/50_mqtt-client
	$(INSTALL_DIR) $(1)/usr/lib/micropython
	$(CP) ./files/micropython-lib/* $(1)/usr/lib/micropython
endef

$(eval $(call BuildPackage,dps-w115))

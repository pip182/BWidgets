#!/bin/bash

# Variables
GTK_THEME="Adwaita-dark"         # Replace with your preferred GTK dark theme
QT5_STYLE="Adwaita-dark"         # Replace with your preferred Qt5 dark theme
QT6_STYLE="Adwaita-dark"         # Replace with your preferred Qt6 dark theme
PLASMA_THEME="BreezeDark"        # Replace with your preferred Plasma theme (if using KDE)

echo "Setting dark theme for GTK..."
gsettings set org.gnome.desktop.interface gtk-theme "$GTK_THEME"
gsettings set org.gnome.desktop.interface color-scheme "prefer-dark"

echo "Setting dark theme for Qt5..."
# Ensure qt5ct is installed and configured
mkdir -p ~/.config/qt5ct
echo -e "[Appearance]\nstyle=$QT5_STYLE\npalette=dark" > ~/.config/qt5ct/qt5ct.conf

echo "Setting dark theme for Qt6..."
# Ensure qt6ct is installed and configured
mkdir -p ~/.config/qt6ct
echo -e "[Appearance]\nstyle=$QT6_STYLE\npalette=dark" > ~/.config/qt6ct/qt6ct.conf

# Environment variable for Qt5
echo "Configuring environment variables for Qt5 and Qt6..."
if ! grep -q "QT_QPA_PLATFORMTHEME" ~/.bashrc; then
    echo 'export QT_QPA_PLATFORMTHEME=qt5ct' >> ~/.bashrc
fi

# Environment variable for Qt6
if ! grep -q "QT_QUICK_CONTROLS_STYLE" ~/.bashrc; then
    echo 'export QT_QUICK_CONTROLS_STYLE=Basic' >> ~/.bashrc
fi

# Set for KDE Plasma (if applicable)
if command -v plasmashell > /dev/null; then
    echo "Setting dark theme for KDE Plasma..."
    lookandfeeltool --apply "$PLASMA_THEME"
fi

# Apply dark theme for terminal (example with GNOME Terminal)
echo "Configuring GNOME Terminal for dark theme..."
PROFILE=$(gsettings get org.gnome.Terminal.ProfilesList default | tr -d "'")
gsettings set "org.gnome.Terminal.Legacy.Profile:/org/gnome/terminal/legacy/profiles:/:$PROFILE/" use-theme-colors false
gsettings set "org.gnome.Terminal.Legacy.Profile:/org/gnome/terminal/legacy/profiles:/:$PROFILE/" background-color "#1E1E1E"
gsettings set "org.gnome.Terminal.Legacy.Profile:/org/gnome/terminal/legacy/profiles:/:$PROFILE/" foreground-color "#D3D3D3"

echo "Dark theme applied successfully!"

# Optional: Refresh environment
echo "You may need to restart your applications or system for changes to take full effect."

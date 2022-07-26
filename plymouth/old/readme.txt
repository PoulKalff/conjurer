# --- Setup Boot Theme -------------------------------------------------------------------
sudo apt install plymouth-themes
sudo cp /conjurer/plymouth/conjurer/ /usr/share/plymouth/themes/ -r
sudo update-alternatives --install /usr/share/plymouth/themes/default.plymouth default.plymouth /usr/share/plymouth/themes/conjurer/conjurer.plymouth 110
sudo update-alternatives --config default.plymouth
        <Vaelg theme>
sudo echo FRAMEBUFFER=y | sudo tee /etc/initramfs-tools/conf.d/splash
sudo update-initramfs -u
sudo init 6



# --- Notes ------------------------------------------------------------------------------
The font used in the logo is called ABBADON, and can be found at "https://www.myfonts.com/fonts/scriptorium/abaddon/abaddon/"












@echo off
echo Re-enabling Windows Firewall...
netsh advfirewall set allprofiles state on
echo Firewall is now enabled.
pause 
@echo off
echo Temporarily disabling Windows Firewall...
netsh advfirewall set allprofiles state off
echo Firewall is now disabled.
echo.
echo IMPORTANT: Remember to re-enable the firewall after testing!
echo.
pause 
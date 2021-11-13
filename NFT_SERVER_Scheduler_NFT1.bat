@echo off
rem NFT_SERVER scheduler
SCHTASKS.EXE /Delete /TN NFT_SERVER /F
@ping 127.0.0.1 -n 2 -w %1000 > nul
SCHTASKS.EXE /CREATE /SC MINUTE /MO 10 /TN "NFT_SERVER" /TR W:\NFT\tools\test\nft_server.bat /RU nft
@ping 127.0.0.1 -n 2 -w %1000 > nul
SCHTASKS.EXE /RUN /TN NFT_SERVER


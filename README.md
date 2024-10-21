# Mullvad VPN Fastest Server Finder
This Python script interacts with the Mullvad VPN CLI and API to help users find and connect to the fastest available VPN server in a specified country. It retrieves the list of Mullvad servers, checks their latency through ping tests, and allows users to connect to the server with the lowest ping time. The script is designed with flexibility in mind, allowing users to specify Max Ping, VPN tunneling protocols (OpenVPN or WireGuard) or leave it open to both.

<img src="https://i.imgur.com/MWjLlJQ.png" alt="Terminal Screen Shot 1" width="300" height="500">

## Key Features
- **Automatic Server Ping Test**: Pings all Mullvad servers in the chosen country and returns the fastest one.
- **Protocol Support**: Allows users to specify the tunneling protocol (OpenVPN or WireGuard) or choose to leave it undefined.
- **Mullvad Connection Check**: Detects if a user is already connected to a Mullvad server, preventing unnecessary server pings.
- **User-Friendly**: Simple command-line prompts to select country, max ping, and protocol.
- **CLI Integration**: Uses the Mullvad CLI to connect or disconnect from servers.

## Prerequisites
- **Mullvad VPN**
- **Python 3.x**
- **Requests library** for fetching server data.

## How to Use
1. Ensure the Mullvad VPN is installed.
2. Run the script. Ex python mullvad_connect.py or run the included batch file (will need to edit run_with_venv.bat to suit your needs)
3. Follow the prompts to select a country, specify the maximum allowed ping (optional), and choose a tunneling protocol (optional).

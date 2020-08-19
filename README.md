# Stock Hawk: 
This is the AWS version of [robinhood_monitor](https://github.com/thevickypedia/robinhood_monitor)

This repo contains scripts that run on lambda connecting to SSM.<br>
Previous Update: Using SSM connector, I got rid of local environment variables which improves secured storage.<br>
Latest update: This script will store information in a 250 digit key (suffixed https://thevickypedia.com/) which is randomly generated each time. This 250 digit key can be accessed by a 16 digit public key on my whats app notifications.

Refer [Wiki](https://github.com/thevickypedia/stock_hawk/wiki) for setup information.

## License & copyright

&copy; Vignesh Sivanandha Rao, Stock Hawk

Licensed under the [MIT License](LICENSE)

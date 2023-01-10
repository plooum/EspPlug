# EspPlug
MicroPython project to inject into an Esp board to control an output over WiFi and BLE.

Ce projet a pour but de mettre à disposition des interfaces de contrôle d'un ESP32 : 
	- un bouton poussoir
	- des commandes via le bluetooth BLE : protocol Nordic UART Service (NUS)
	- des commandes via une interface web : via l'envoi de paramètres GET
	Le but est de contrôler une sortie (par exemple un relais pour faire une prise connectée)

Installer Micropython (Obtenir un environnement de développement et flasher la carte ESP32)
	
	1-Installer les drivers usb (CP210x Windows Drivers)
		https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers?tab=downloads

	2-Télécharger le firmware pour MicroPython (version testée v1.19.1)
		Pour les ESP8266 des SONOFF : https://micropython.org/download/esp8266-1m/
		
		Pour les ESP32 : https://micropython.org/download/esp32/
		
	3-Installer l’IDE Thonny 
		https://github.com/thonny/thonny/releases/tag/v4.0.1
	
	4-Brancher l'ESP32 et identifier son numéro de port (port COM sous windows).
	
	5-L’installer et le configurer : Onglet Exécuter > Configurer linterpréteur > Onglet Interpréteur choisir MicroPython(esp32).
		Sélectionner le port.
		Puis cliquer sur « Install or update… », sélectionner le port et le firmware et lancer le flash du firmware.
		Enfin cliquer sur OK et l’interpréteur devrait être connecté.

	6-Envoyer le code MicroPython vers la carte
		6.1-Afficher la fenêtre "Fichier" : Cliquer sur le menu "Affichage" puis cocher "Fichiers".
		6.2-La fenêtre s'affiche à gauche de l'environnement.
		6.3-Dans la partie supérieure de la fenêtre de gauche, se rendre dans le répertoire où les fichiers du projet ont été téléchargés.
		6.4-Dans cette même zone, sélectionner tous les fichiers (à l'aide de la touche "Shift") puis faire un clic droit puis cliquer sur "Téléversement vers /" (sans doute upload en anglais).
	
	7-Pour démarrer le programme, cliquer le bouton "Stop" en rouge dans la barre de menu supérieure (ou faire Ctrl+F2).
		Ou appuyer sur le bouton de gauche de la carte ESP.
	
	8-Pour arrêter l'exécution du programme, s'assurer que rien n'est sélectionné puis faire Ctrl+C.

Procédure pour le premier paramétrage

	- Installer l'application Serial Bluetooth Terminal sur un smartphone.
	- Démarrer le programme sur l'ESP.
	- Démarrer l'appli Serial Bluetooth Terminal.
		- Activer le bluetooth et la localisation du smartphone.
		- Appuyer sur le bouton menu, puis cliquer sur Devices.
		- En haut, cliquer sur SCAN.
		- L'ESP devrait apparaître sous son nom par défaut "ESP32".
		- Cliquer dessus.
		- Connected devrait apparaître en jaune dans le terminal.
		- Activer le DEBUG pour pouvoir suivre la bonne exécution des commandes (depuis widows) :
			- Envoyer la commande s_debug=1;
				 -A chaque commande reçue et interprétée par l'ESP, le message OK doit apparaître en vert dans le terminal.
			- Envoyer la commande save;
			- Envoyer la commande restart;
				- Attendre une dizaine de secondes.
		- Un message "Connection lost" devrait apparaître.
		- Se reconnecter à l'ESP (via le bouton en haut à droite).
		- Affecter une IP à l'ESP :
			- Choisir une IP compatible avec le réseau :
				- Depuis Windows, ouvrir une invite de commande et taper la commande ipconfig.
					- Identifier le réseau local et retenir l'IP du pc (sous la forme 192.168.1.xxx ou 192.168.0.xxx)
				- Choisir une ip similaire à celle du PC (mon IP est 192.168.1.21, dans l'exemple qui suivra, je vais choisir 192.168.1.152)
			- Envoyer la commande s_ip=192.168.1.152
		- Configurer le nom du point d'accès WIFI (par exemple SFR_42) :
			- Envoyer la commande s_ssid=SFR_42;
		- Configurer le mot de passe d'accès au WIFI (par exemple 12345678) :
			- Envoyer la commande s_pass=12345678;
		- Enregistrer
			- Envoyer la commande save;
		- Redémarrer l'ESP :
			- Envoyer la commande restart;
		- L'ESP devrait afficher les messages suivants dans la console série:
			- WIFI : Connected
			- Main : Starting WebServer
			- WebServer : Started
		- Ensuite, ouvrir un navigateur web et saisir l'adresse ip choisie.
		- La liste des commandes y est affichée. Il est possible de les tester. Un message de retour apparaîtra en dessous après exécution de la commande.
		
		- Les commandes web sont exécutables via des requêtes get dont l'url est l'identifiant de la commande. 
		- Il ne peut y avoir qu'une valeur du paramètre GET. Cette valeur est séparée du nom du paramètre par un signe "=".
		- Ce signe est paramétrable. Ce paramètre s'appelle "cmd_separator" dans la configuration.
			- exemple de requête pour allumer la sortie (script JS) : 
				var xhr = new XMLHttpRequest();
                xhr.open("GET", "192.168.1.152/?s_on", true);
                xhr.onload = function(e) {
                    var s = xhr.responseText;
					// s devrait contenir "OK" ici
                }
                xhr.send();
			- exemple de requête pour changer le nom Bluetooth de l'ESP (script JS) : 
				var xhr = new XMLHttpRequest();
                xhr.open("GET", "192.168.1.152//?s_ble=ESP_lumiere_salon", true);
                xhr.onload = function(e) {
                    var s = xhr.responseText;
					// s devrait contenir "OK" ici
                }
                xhr.send();
			- exemple de requête pour récupérer la configuration (script JS) : 
				var xhr = new XMLHttpRequest();
                xhr.open("GET", "192.168.1.152///?g_config", true);
                xhr.onload = function(e) {
                    var s = xhr.responseText;
					// s devrait contenir la configuration : un argument par ligne séparé de sa valeur par "="
                }
                xhr.send();
-----------		
- Fonctionnalités disponibles
	- WIFI
		- Connexion à une box WIFI
	- Serveur WEB
		- Commandes via des requêtes GET
		- Liste de commandes disponibles affichées sur la page web de la racine (les commandes sont aussi valables pour le Bluetooth BLE)
		- Les commandes sont testables depuis l'interface web
	- IP Fixe
	- Config dans le fichier de config
	- Fichier de config interchangeable : possibilité de passer d'une config à une autre via des commandes
	- Bluetooth BLE
		- Possibilité de se connecter via l'appli Bluetooth Serial Terminal.
		- L'envoi de commande est possible
		- Envoyer des commandes pour modifier les paramètres de config.
		- Envoyer des commandes pour autre chose, cf. liste de commandes.
	- Bouton par "Interruption" cf. IRQ
		- Active/Désactive la sortie
		
- Fonctionnalités à développer
	- WIFI
		- Faire office de "Box WIFI" pour permettre de se connecter lorsque les paramètres de connexion à la Box ne sont pas définis.
		- Pouvoir utiliser le DHCP et afficher son ip par exemple en BLE
	
- Remarques
	- Ne pas utiliser des threads pour des fonctionnalités qui fonctionnent en continu
		- Après plusieurs essais, j'en suis venu à la conclusion que les threads peuvent interrompre les foncionnalités qui ont besoin des IRQ (notamment le bluetooth)
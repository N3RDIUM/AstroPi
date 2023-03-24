<img src="https://user-images.githubusercontent.com/74598401/225719282-0c3ecc35-4f5f-4f5d-8ac1-f31d5439f2c6.png" style="align-self: center; justify-self: center; width:100%;"></img>

<h1 align="center">AstroPi</h1>

<p align="center">A DIY astronomy camera made with a raspberry pi 3b+ and the PiCamera v3! This project is in its pre beta stage. </p>

If you're the cheap type of amateur astronomer, I know you'd rather make your own astrophotography camera than buy one. This project is for you! This project is a DIY astrophotography camera made with a raspberry pi 3b+ and the PiCamera v3. This project is in its pre beta stage.

## Overview
This project has been tested on a Raspberry Pi 3b+ and PiCamera v3. It is not guaranteed to work on other versions of the Pi or the PiCamera. Testing on other versions of the Pi and PiCamera is welcome.

## Demo
Coming soon!

## Features
- [x] Control the camera remotely
- [x] Live preview via a web browser widget
- [x] Manual focus, Gain, and exposure control
- [ ] Monitor the temperature of the camera

## Materials
- Raspberry Pi 3b+
- PiCamera v3
- Raspberry Pi 3b+ case (with fan slot)
- An extra fan (for cooling the camera)
- A laptop or desktop computer
- Loooooong Ethernet cable

## Build your AstroPi
Please follow the instructions in my blog post [here](astropi.n3rdium.dev/setup) to set up your AstroPi.

## Usage
I've made a light application to control your AstroPi. It's available on Linux and Windows. Sorry, Mac users! Support is coming soon. You can download the application [here](astropi.n3rdium.dev/download).

## Contributing
Contributions are welcome! Please read the [contributing guidelines](CONTRIBUTING.md) before contributing.

# TODO
## NON-CODE
- [ ] Write the installation instructions
- [ ] Write the usage instructions
- [ ] Write the contributing guidelines
- [ ] Create a demo video
- [ ] Create some sample images
- [ ] Design the camera and cooling fan housing for 3d prints
##  CODE
- [ ] Create a startup script for the raspberry pi which runs git pull and starts the server
- [x] Stream to socket, get live preview
- [ ] Create setup for windows, linux
- [ ] Create setup for mac (maybe?)
- [ ] Create a mobile app (for travellers)
- [ ] Create a web app (for remote control)

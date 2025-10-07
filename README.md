# OPC-UA-Server-for-Camera
Sample Python application that provides access to the camera image over OPC UA Server interface

## Prerequisites

Install dependency Python modules:

```
pip install opencv-python
pip install opcua
```

## How to run

Open command line terminal, navigate to the repository folder, and run the command:

```
python OpcUaServer.py
```

As a result, OPC UA Server should start and listen on port 4840.

## How to view the image on UA Expert (OPC UA Client).


- Start UA Expert and connect to the server 

- Select the menu ``Document / Add``, and add new document of the ``Image Viewer`` type. It will add new tab in the central panel.

- Browse address space of the server, navigate to the node ``Objects / Camera Device / Camera Image``.

- Drag and drop the selected variable node from address space to the image viewer panel. Now you should see the image displayed in UA Expert.

## Troubleshooting

### The OPC UA Server failes to start

This can happen is the default port 4840 is used by other application. To resolve, change the port number in OPC UA Server code, or close the application that uses this port.

### The server cannot have access to the camera.

Check if operating system settings allow access to the camera by desktop applications. In Windows, open ``Settings / Privacy & Security / Camera``, and turn ON the option ``Let desktop apps access your camera``.

If the option is already ON, check in the same dialog window, if some other application is using camera.

## TODO

- Detect all cameras in the host and add them to the address space.
- Add properties showing if a camera is in use, and other available properties.
- Take snapshots only when clients are requesting either to read the image, or added monitored item for the camera variable. If the client is subscribed, then take snapshots with interval defined by the monitored item sampling interval, and apply percentage based deadband. Applying deadband will reduce bandwidth as the server would publish new image only when it the difference comparing to the previously published snapshot image is greater than deadband percentage.
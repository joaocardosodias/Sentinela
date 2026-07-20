---
sidebar_position: 1
---

# Código do Drone

&emsp; Nesta documentação será responsável por deixar em escrito o passo a passo da procura e das decisões tomadas pelo grupo sobre a conexão do drone com o computador. 

## Passo 1 - Como se Usa o Drone Hoje?

&emsp; Hoje, o drone DJI Tello é controlado pelo app dele, via Wifi, chamado Tello. Nele, apenas tem a interface de conexão do drone e quando conecta, aparece a câmera com seus controles. O nosso objetivo essa sprint é fazer com que não dependemos mais desse aplicativo e controlamos tudo pelo computador via Wifi por código. 

## Passo 2 - Encontrar Código para Conexão Inicial

&emsp; Em uma pesquisa na internet, conseguimos encontrar o código responsável pela conexão e meio de conversa entre o drone e o computador. Esse código é chamado de *Tello.py*  e foi achado no seguinte arquivo: https://terra-1-g.djicdn.com/2d4dce68897a46b19fc717f3576b7c6a/Tello%20%E7%BC%96%E7%A8%8B%E7%9B%B8%E5%85%B3/For%20Tello/Tello%20SDK%20Documentation%20EN_1.3_1122.pdf

&emsp; Com esse código, apenas deveriamos conectar-se com a internet do drone e rodar nosso código no terminal para que conseguissimos se comunicar com o drone.

## Passo 3 - Comunicação e Câmera do Drone

&emsp; Nosso desafio era pegar a câmera que estava sendo mostrada no app do Tello e jogar para o computador. Assim, fizemos um código, usando a biblioteca *cv2*, para que: quando rodarmos "streamon", uma janela com a visão da câmera seria aberta no PC, concluindo a task. As funções que controlam o drone pelo terminal está no seguinte arquivo: https://dl-cdn.ryzerobotics.com/downloads/Tello/Tello%20SDK%202.0%20User%20Guide.pdf 

&emsp; O fluxo de conversa com o drone para abrir a tal janela no seu PC é:

1. Conexão com a internet do drone.
2. Rodar o código em que o Tello.py foi colocado, no nosso caso é o *drone.py*.
3. Usar o comando "command", responsável por abrir a conexão dos comando entre PC e drone.
4. Digitar no terminal "streamon" para olhar a câmera pelo PC.

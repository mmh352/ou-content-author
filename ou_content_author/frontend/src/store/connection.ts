import { writable, derived } from "svelte/store";

const INITIALISING = 0;
const READY = 1;
const DISCONNECTED = 2;

let connection = null;

export const message = writable(null as Message);

export const connectionStatus = writable(INITIALISING);

export const isInitialising = derived(connectionStatus, (connectionStatus) => {
    return connectionStatus === INITIALISING;
});

export const isReady = derived(connectionStatus, (connectionStatus) => {
    return connectionStatus === READY;
});

export const isDisconnected = derived(connectionStatus, (connectionStatus) => {
    return connectionStatus === DISCONNECTED;
});

export function connect() {
    const basepath = document.querySelector('body').getAttribute('data-basepath');
    if (window.location.protocol === 'https:') {
        connection = new WebSocket('wss://' + window.location.hostname + ':' + window.location.port + basepath + '../api');
    } else {
        connection = new WebSocket('ws://' + window.location.hostname + ':' + window.location.port + basepath + '../api');
    }
    connection.addEventListener('open', () => {
        connectionStatus.set(READY);
    });
    connection.addEventListener('close', () => {
        connectionStatus.set(DISCONNECTED);
    });
    connection.addEventListener('message', (msg) => {
        if (msg.data) {
            message.set(JSON.parse(msg.data));
        }
    });
}

export function sendMessage(msg: Message) {
    if (connection) {
        connection.send(JSON.stringify(msg));
    }
}

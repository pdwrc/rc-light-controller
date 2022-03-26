import { splitOnSpace } from "./util.js";

export class LCSerialCommandError extends Error {

}

export class LCSerial {
    constructor(port) {
        this.serialPort = port;
        this.reader = null;
        this.bufIn = '';
        this.lines = [];
        this.responseCallbacks = {};
    }

    open(closedCallback) {
        return this.serialPort.open({baudRate: 115200}).then(() => {
            console.log("Opening");
            this.readUntilClosed(closedCallback);
            console.log("Closed");
        });
    }

    async serialWrite(msg) {
        const encoder = new TextEncoder();
        if (this.serialPort.writable.locked) {
            console.log("Writer locked");
            return;
        }
        const writer = this.serialPort.writable.getWriter();
        await writer.write(encoder.encode(msg));
        writer.releaseLock();
    }

    async readUntilClosed(closedCallback) {
        const decoder = new TextDecoder();
        this.reader = this.serialPort.readable.getReader();

        var newLines = [];

        try {
            while (true) {
                const { value, done } = await this.reader.read();
                if (done) {
                    console.log("Closing");
                    break;
                }
                this.bufIn += decoder.decode(value);
                newLines = this.bufIn.replace('\r','').split('\n');
                console.log(newLines);
                for (var i = 0; i < newLines.length - 1; i++) {
                    var cmd;
                    var args;
                    if (newLines[i].includes(' ')) {
                        const parts = splitOnSpace(newLines[i]);
                        cmd = parts[0];
                        args = parts[1];
                    }
                    else {
                        cmd = newLines[i];
                    }

                    if (this.responseCallbacks[cmd] !== undefined) {
                        this.responseCallbacks[cmd](args);
                    }
                    this.lines.push(newLines[i])
                }
                this.bufIn = newLines[newLines.length-1];
            }
        }
        catch (error) {
            console.log(error);
        }
        finally {
            this.reader.releaseLock();
        }
        await this.serialPort.close();
        closedCallback();
    }

    addCallback(cmd, cb) {
        this.responseCallbacks[cmd] = cb;
    }
    
    removeCallback(cmd) {
        delete this.responseCallbacks[cmd];
    }

    doCommand(cmd) {
        return new Promise((resolve, reject) => {
            this.addCallback(cmd, (data) => {
                this.removeCallback(cmd);
                resolve(data)
            });
            this.addCallback("ERR", () => {
                this.removeCallback("ERR");
                reject(new LCSerialCommandError("Command returned error"))
            });
            this.serialWrite(cmd + "\n");
            console.log(cmd+"\n");
        });
    }

    async close() {
        return this.reader.cancel();
    }

}

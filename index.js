import fetch from 'node-fetch';

// ---------- Insert Your Data ---------- //
const BOT_TOKEN = "5471483205:AAHOgy6y5LzxOJJ42znF4Kr_SfaW7Ic9oFc"; // Insert your bot token.
const BOT_SECRET = "BOT_SECRET"; // Insert a powerful secret text.
const BOT_OWNER = 834554042; // Insert your telegram account id.
const BOT_CHANNEL = -1001734249184; // Insert your telegram channel id.
const SIA_SECRET = "SIA_SECRET"; // Insert a powerful secret text.
const PUBLIC_BOT = false; // Make your bot public.

// ---------- Constants ---------- //
const WHITE_METHODS = ["GET", "POST", "HEAD"];
const MAX_FILE_SIZE = 4 * 1024 * 1024 * 1024; // 4 GB
const CACHE_TTL = 60 * 60; // 1 hour cache TTL
const ERROR_404 = {
    "ok": false,
    "error_code": 404,
    "description": "Bad Request: missing /?file= parameter",
    "credit": "https://github.com/vauth/filestream-cf"
};
const ERROR_405 = {
    "ok": false,
    "error_code": 405,
    "description": "Bad Request: method not allowed"
};
const ERROR_406 = {
    "ok": false,
    "error_code": 406,
    "description": "Bad Request: file type invalid"
};
const ERROR_407 = {
    "ok": false,
    "error_code": 407,
    "description": "Bad Request: file hash invalid by atob"
};
const ERROR_408 = {
    "ok": false,
    "error_code": 408,
    "description": "Bad Request: mode not in [attachment, inline]"
};
const ERROR_409 = {
    "ok": false,
    "error_code": 409,
    "description": "Bad Request: file size exceeds limit"
};

// ---------- Hash Generator ---------- //
class Cryptic {
    static async getSalt(length = 16) {
        const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        let salt = '';
        for (let i = 0; i < length; i++) {
            salt += characters.charAt(Math.floor(Math.random() * characters.length));
        }
        return salt;
    }

    static async getKey(salt, iterations = 1000, keyLength = 32) {
        const key = new Uint8Array(keyLength);
        for (let i = 0; i < keyLength; i++) {
            key[i] = (SIA_SECRET.charCodeAt(i % SIA_SECRET.length) + salt.charCodeAt(i % salt.length)) % 256;
        }
        for (let j = 0; j < iterations; j++) {
            for (let i = 0; i < keyLength; i++) {
                key[i] = (key[i] + SIA_SECRET.charCodeAt(i % SIA_SECRET.length) + salt.charCodeAt(i % salt.length)) % 256;
            }
        }
        return key;
    }

    static async baseEncode(input) {
        const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567';
        let output = '';
        let buffer = 0;
        let bitsLeft = 0;
        for (let i = 0; i < input.length; i++) {
            buffer = (buffer << 8) | input.charCodeAt(i);
            bitsLeft += 8;
            while (bitsLeft >= 5) {
                output += alphabet[(buffer >> (bitsLeft - 5)) & 31];
                bitsLeft -= 5;
            }
        }
        if (bitsLeft > 0) {
            output += alphabet[(buffer << (5 - bitsLeft)) & 31];
        }
        return output;
    }

    static async baseDecode(input) {
        const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567';
        const lookup = {};
        for (let i = 0; i < alphabet.length; i++) {
            lookup[alphabet[i]] = i;
        }
        let buffer = 0;
        let bitsLeft = 0;
        let output = '';
        for (let i = 0; i < input.length; i++) {
            buffer = (buffer << 5) | lookup[input[i]];
            bitsLeft += 5;
            if (bitsLeft >= 8) {
                output += String.fromCharCode((buffer >> (bitsLeft - 8)) & 255);
                bitsLeft -= 8;
            }
        }
        return output;
    }

    static async Hash(text) {
        const salt = await this.getSalt();
        const key = await this.getKey(salt);
        const encoded = String(text).split('').map((char, index) => {
            return String.fromCharCode(char.charCodeAt(0) ^ key[index % key.length]);
        }).join('');
        return await this.baseEncode(salt + encoded);
    }

    static async deHash(hashed) {
        const decoded = await this.baseDecode(hashed);
        const salt = decoded.substring(0, 16);
        const encoded = decoded.substring(16);
        const key = await this.getKey(salt);
        const text = encoded.split('').map((char, index) => {
            return String.fromCharCode(char.charCodeAt(0) ^ key[index % key.length]);
        }).join('');
        return text;
    }
}

// ---------- Telegram Bot ---------- //
class Bot {
    static async getMe() {
        const response = await fetch(`https://api.telegram.org/bot${BOT_TOKEN}/getMe`);
        if (response.status == 200) return (await response.json()).result;
        else return await response.json();
    }

    static async sendMessage(chat_id, text) {
        const response = await fetch(`https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ chat_id, text })
        });
        if (response.status == 200) return (await response.json()).result;
        else return await response.json();
    }
}

// ---------- Main Function ---------- //
async function main() {
    console.log("Starting bot...");
    const botInfo = await Bot.getMe();
    console.log("Bot Info:", botInfo);

    // Example: Send a message to the owner
    await Bot.sendMessage(BOT_OWNER, "Hello from GitHub Actions!");
    console.log("Message sent!");
}

main().catch(error => {
    console.error("Error in main function:", error);
});

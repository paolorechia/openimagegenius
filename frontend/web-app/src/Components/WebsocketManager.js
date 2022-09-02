

export default function WebsocketManager() {
    const ws_endpoints = {
        "dev": "wss://dev.ws-api.openimagegenius.com"
    }
    function getTokenCookie() {
        let decodedCookie = decodeURIComponent(document.cookie);
        const cookies = decodedCookie.split(";")
        console.log(cookies)
        const maybe_tokens = cookies.map(cookie => {
            const cookie_name = cookie.split("=")[0].trim()
            if (cookie_name === "token") {
                return cookie.split("=")[1].trim()
            }
            return null
        })
        const filtered_maybe_tokens = maybe_tokens.filter(token => token !== null)
        if (filtered_maybe_tokens.length === 1) {
            return filtered_maybe_tokens[0]
        }
        if (filtered_maybe_tokens.length === 0) {
            return null
        }
        console.error("Multiple cookies found, not sure what to do!");
        return -1
    }
    let token = null;
    token = getTokenCookie()
    console.log("Your token is: ", token)
    if (token === null) {
        // Unauthorized, handle redirect.
    }
    if (token === -1) {
        // Oh no, do something about this
    }
    const websocket = new WebSocket(ws_endpoints["dev"])
    return websocket
} 
import httpProxy from 'http-proxy';

// Create a proxy server
const proxy = httpProxy.createProxyServer();

export default function handler(req, res) {
  // Proxy the request to the backend service
  proxy.web(req, res, { target: 'http://backend-service' });
}

export const config = {
  api: {
    bodyParser: false, // Disable body parsing, since we are proxying requests
  },
};

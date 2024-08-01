import httpProxy from 'http-proxy';

// Create a proxy server
const proxy = httpProxy.createProxyServer();

export async function POST(req) {
  return new Promise((resolve, reject) => {
    req.url = req.url.replace(/^\/api\/proxy/, ''); // Adjust URL path if needed

    proxy.web(req, {
      target: 'http://backend-service',
      changeOrigin: true,
    }, (error) => {
      if (error) {
        reject(error);
      } else {
        resolve(new Response(null, { status: 200 }));
      }
    });
  });
}

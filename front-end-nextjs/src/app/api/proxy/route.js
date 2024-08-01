import { NextResponse } from 'next/server';

export async function POST(req) {
  return await handleProxy(req);
}

async function handleProxy(req) {

  const body = await req.json();
  const {url} = body;
  //use /backend/ instead of /backend-service.default.svc.cluster.local:8000 for development
  const backendUrl = `http://backend-service.default.svc.cluster.local:8000/generate-qr/?url=${url}`;

  const response = await fetch(backendUrl , {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    return NextResponse.json({
      status: response.status,
      body: await response.text(),
    } , {status: 500});
  }

  const data = await response.json();
  console.log(data);
  return NextResponse.json({data: data.qr_code_url});
  
}

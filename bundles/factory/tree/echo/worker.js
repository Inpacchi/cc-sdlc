// The factory's echo service as a Cloudflare Worker (z-sdlc factory bundle; factory.json's smoke.echo_host).
// factory-smoke's credential-mask and services jobs send throwaway credentials through the agent sandbox's
// proxy to this host and read the echoed request headers, one per line, to prove the proxy injected them.
// It answers any request with its method, URL, query arguments and headers as indented JSON, and stores
// nothing. Deploy it on a workers.dev address (no zone bot protection there), then set smoke.echo_host.
export default {
  async fetch(request) {
    const url = new URL(request.url);
    const headers = {};
    for (const [name, value] of request.headers) {
      headers[name.replace(/(^|-)([a-z])/g, (_, dash, c) => dash + c.toUpperCase())] = value;
    }
    const body = { args: Object.fromEntries(url.searchParams), headers, method: request.method, url: request.url };
    return new Response(JSON.stringify(body, null, 2) + "\n", {
      headers: { "content-type": "application/json", "cache-control": "no-store" },
    });
  },
};

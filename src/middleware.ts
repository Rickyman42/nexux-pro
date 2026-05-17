import { defineMiddleware } from 'astro:middleware';

const SEC: Record<string, string> = {
  'X-Content-Type-Options': 'nosniff',
  'X-Frame-Options': 'SAMEORIGIN',
  'Referrer-Policy': 'strict-origin-when-cross-origin',
  'Permissions-Policy': 'camera=(), microphone=(), geolocation=()',
};

function sec(r: Response): Response {
  for (const [k, v] of Object.entries(SEC)) r.headers.set(k, v);
  return r;
}

function getClientIdFromPath(pathname: string) {
  const match = pathname.match(/^\/cliente\/([^/]+)/);
  return match?.[1] ?? null;
}

export const onRequest = defineMiddleware(async (context, next) => {
  const url = new URL(context.request.url);
  const pathname = url.pathname;

  if (pathname.startsWith('/api/') || pathname === '/health') {
    return sec(await next());
  }

  if (!pathname.startsWith('/cliente/')) {
    return sec(await next());
  }

  const clientId = getClientIdFromPath(pathname);
  if (!clientId) {
    return sec(await next());
  }

  const isLoginRoute = pathname.endsWith('/login');
  const queryToken = url.searchParams.get('t');
  const cookieToken = context.cookies.get('nexux_token')?.value;

  if (queryToken) {
    context.cookies.set('nexux_token', queryToken, {
      maxAge: 60 * 60 * 24 * 30,
      httpOnly: true,
      secure: true,
      sameSite: 'lax',
      path: '/',
    });
    context.cookies.set('nexux_client', clientId, {
      maxAge: 60 * 60 * 24 * 30,
      httpOnly: true,
      secure: true,
      sameSite: 'lax',
      path: '/',
    });

    url.searchParams.delete('t');
    return sec(context.redirect(`/cliente/${clientId}${url.search ? url.search : ''}`));
  }

  if (!cookieToken) {
    if (isLoginRoute) return sec(await next());
    return sec(context.redirect(`/cliente/${clientId}/login`));
  }

  if (isLoginRoute) {
    return sec(context.redirect(`/cliente/${clientId}`));
  }

  return sec(await next());
});

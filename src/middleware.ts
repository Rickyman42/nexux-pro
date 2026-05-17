import { defineMiddleware } from 'astro:middleware';

function getClientIdFromPath(pathname: string) {
  const match = pathname.match(/^\/cliente\/([^/]+)/);
  return match?.[1] ?? null;
}

export const onRequest = defineMiddleware((context, next) => {
  const url = new URL(context.request.url);
  const pathname = url.pathname;

  if (pathname.startsWith('/api/') || pathname === '/health') {
    return next();
  }

  if (!pathname.startsWith('/cliente/')) {
    return next();
  }

  const clientId = getClientIdFromPath(pathname);
  if (!clientId) {
    return next();
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
    return context.redirect(`/cliente/${clientId}${url.search ? url.search : ''}`);
  }

  if (!cookieToken) {
    if (isLoginRoute) return next();
    return context.redirect(`/cliente/${clientId}/login`);
  }

  if (isLoginRoute) {
    return context.redirect(`/cliente/${clientId}`);
  }

  return next();
});

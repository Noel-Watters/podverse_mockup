import { NextResponse } from "next/server";
import { auth0 } from "./lib/auth0"


export async function middleware(request) {
    const authRes = await auth0.middleware(request);

    // authentication routes — let the middleware handle it
    if (request.nextUrl.pathname.startsWith("/auth")) {
        return authRes;
    }


    // allow public static files (SVG, images, etc.) to bypass auth
    const publicFilePattern = /^\/(.*\.(svg|png|jpg|jpeg|gif|ico|webp|css|js))$/i;
    if (request.nextUrl.pathname === "/" || publicFilePattern.test(request.nextUrl.pathname)) {
        return authRes;
    }

    const session = await auth0.getSession();
    if (!session) {
        const { origin } = new URL(request.url);
        return NextResponse.redirect(`${origin}/auth/login?returnTo=/dashboard`);
    }

} 

export const config = {
    matcher: [
        /*
         * Match all request paths except for the ones starting with:
         * - _next/static (static files)
         * - _next/image (image optimization files)
         * - favicon.ico, sitemap.xml, robots.txt (metadata files)
         * - api (API routes)
         */
        "/((?!_next/static|_next/image|favicon.ico|sitemap.xml|robots.txt|api).*)",
    ],
}

export const runtime = 'nodejs';
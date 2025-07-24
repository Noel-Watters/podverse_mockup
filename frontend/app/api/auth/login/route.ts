// Workaround for broken type declarations
const loginHandler = require('@auth0/nextjs-auth0/edge/handlers/login').default;

export const GET = loginHandler;

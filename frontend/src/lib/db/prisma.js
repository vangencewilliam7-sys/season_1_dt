/**
 * src/lib/db/prisma.js
 *
 * Prisma Client singleton for Next.js.
 *
 * Next.js hot-reload creates new module instances in development,
 * which would open a new DB connection on every reload and exhaust
 * the connection pool. This singleton pattern prevents that.
 *
 * Usage:
 *   import { prisma } from '@/lib/db/prisma'   (or relative import)
 *   const chunks = await prisma.documentChunk.findMany({ where: { expertId } })
 */

import { PrismaClient } from '@prisma/client'

const globalForPrisma = globalThis

export const prisma =
  globalForPrisma.prisma ??
  new PrismaClient({
    log: process.env.APP_ENV === 'development'
      ? ['query', 'error', 'warn']
      : ['error'],
  })

if (process.env.NODE_ENV !== 'production') {
  globalForPrisma.prisma = prisma
}

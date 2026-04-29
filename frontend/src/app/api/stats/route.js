/**
 * src/app/api/stats/route.js
 *
 * GET /api/stats?expertId=<uuid>
 *
 * Returns dashboard stat counts from the DB via Prisma.
 * Called by the dashboard page on mount.
 */

import { NextResponse } from 'next/server'
import { getDashboardStats } from '../../../lib/db/queries'

export const dynamic = 'force-dynamic'

export async function GET(request) {
  try {
    const { searchParams } = new URL(request.url)
    const expertId = searchParams.get('expertId') ?? 'demo'

    const stats = await getDashboardStats(expertId)

    return NextResponse.json(stats)
  } catch (error) {
    console.error('[/api/stats] Error:', error.message)
    return NextResponse.json(
      { error: 'Failed to fetch stats', detail: error.message },
      { status: 500 }
    )
  }
}

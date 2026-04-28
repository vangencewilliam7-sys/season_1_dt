/**
 * src/lib/db/queries.js
 *
 * Typed query helpers for the Digital Twin database.
 *
 * SOLID — Single Responsibility
 * Each function does exactly one thing. Callers never write raw Prisma
 * queries — they call these named functions.
 *
 * All functions are async and return typed results from Prisma.
 */

import { prisma } from './prisma'


// ── Knowledge Hub ──────────────────────────────────────────────────────────────

/**
 * Get all document chunks for an expert, ordered by hierarchy.
 */
export async function getChunksByExpert(expertId) {
  return prisma.documentChunk.findMany({
    where: { expertId },
    orderBy: [{ level: 'asc' }, { createdAt: 'asc' }],
  })
}

/**
 * Get children of a specific chunk (one level down in hierarchy).
 */
export async function getChildChunks(parentId) {
  return prisma.documentChunk.findMany({
    where: { parentId },
    orderBy: { createdAt: 'asc' },
  })
}

/**
 * Get all Master Cases for an expert, newest first.
 */
export async function getMasterCasesByExpert(expertId) {
  return prisma.masterCase.findMany({
    where: { expertId },
    include: { sourceChunk: true },
    orderBy: { createdAt: 'desc' },
  })
}

/**
 * Get only active (non-superseded) master cases for an expert.
 */
export async function getActiveMasterCases(expertId) {
  return prisma.masterCase.findMany({
    where: {
      expertId,
      supersededBy: null,
    },
    orderBy: { createdAt: 'desc' },
  })
}

/**
 * Get unresolved decision gaps (implicit knowledge waiting to surface).
 */
export async function getUnresolvedGaps() {
  return prisma.decisionGap.findMany({
    where: { resolved: false },
    include: { sourceChunk: true },
    orderBy: { createdAt: 'desc' },
  })
}


// ── Expert Persona ─────────────────────────────────────────────────────────────

/**
 * Get the latest approved PersonaManifest for an expert.
 * Returns null if no approved manifest exists yet.
 */
export async function getApprovedManifest(expertId) {
  return prisma.personaManifest.findFirst({
    where: {
      expertId,
      shadowApproved: true,
    },
    orderBy: { manifestVersion: 'desc' },
  })
}

/**
 * Get all manifests for an expert (including drafts), newest first.
 */
export async function getAllManifests(expertId) {
  return prisma.personaManifest.findMany({
    where: { expertId },
    orderBy: { manifestVersion: 'desc' },
  })
}

/**
 * Get all manifests pending Shadow Mode review.
 */
export async function getPendingManifests() {
  return prisma.personaManifest.findMany({
    where: { shadowApproved: false },
    orderBy: { createdAt: 'desc' },
  })
}


// ── Pipeline State ─────────────────────────────────────────────────────────────

/**
 * Get the LangGraph state for a specific session.
 */
export async function getPipelineState(sessionId) {
  return prisma.pipelineState.findUnique({
    where: { sessionId },
  })
}

/**
 * Get all active (running or paused) pipeline sessions for an expert.
 */
export async function getActivePipelines(expertId) {
  return prisma.pipelineState.findMany({
    where: {
      expertId,
      status: { in: ['running', 'paused'] },
    },
    orderBy: { updatedAt: 'desc' },
  })
}


// ── Skills Audit Log ───────────────────────────────────────────────────────────

/**
 * Get recent skill executions for an expert (last 50).
 */
export async function getRecentSkillExecutions(expertId, limit = 50) {
  return prisma.skillExecution.findMany({
    where: { expertId },
    orderBy: { executedAt: 'desc' },
    take: limit,
  })
}

/**
 * Get skill execution stats — success rate per skill.
 */
export async function getSkillStats(expertId) {
  const executions = await prisma.skillExecution.groupBy({
    by: ['skillId'],
    where: { expertId },
    _count: { success: true },
    _sum: { success: true },
  })
  return executions
}


// ── Dashboard Stats ────────────────────────────────────────────────────────────

/**
 * Aggregate counts for the dashboard stat cards.
 * Single DB round-trip using Promise.all.
 */
export async function getDashboardStats(expertId) {
  const [chunks, cases, manifests, gaps] = await Promise.all([
    prisma.documentChunk.count({ where: { expertId } }),
    prisma.masterCase.count({ where: { expertId, supersededBy: null } }),
    prisma.personaManifest.count({ where: { expertId, shadowApproved: true } }),
    prisma.decisionGap.count({ where: { resolved: false } }),
  ])

  return {
    documentsIngested: chunks,
    masterCases: cases,
    personaManifests: manifests,
    knowledgeGapsFlagged: gaps,
  }
}

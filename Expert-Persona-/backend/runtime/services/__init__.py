# runtime/services/ — Knowledge Hub Integration Services
#
# Thin service wrappers that connect Expert-Persona to the
# Knowledge Hub's Supabase-backed Logic Vault.
#
# These services are used by:
#   - SupabaseReader (reads document_chunks for extraction pipeline)
#   - retrieve_context_node (queries expert_dna for conversation runtime)

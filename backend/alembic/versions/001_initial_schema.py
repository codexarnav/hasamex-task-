"""Initial schema migration for InsightOS V1.

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-09-24 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Projects
    op.create_table(
        'projects',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('objective', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_projects_status', 'projects', ['status'])

    # 2. Interview Guides
    op.create_table(
        'interview_guides',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('source_file', sa.String(length=500), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_interview_guides_project_id', 'interview_guides', ['project_id'])

    # 3. Research Questions
    op.create_table(
        'research_questions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('guide_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('interview_guides.id', ondelete='CASCADE'), nullable=False),
        sa.Column('question_number', sa.Integer(), nullable=False),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_research_questions_project_id', 'research_questions', ['project_id'])
    op.create_index('ix_research_questions_guide_id', 'research_questions', ['guide_id'])

    # 4. Experts
    op.create_table(
        'experts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=255), nullable=True),
        sa.Column('market', sa.String(length=255), nullable=True),
        sa.Column('organization', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_experts_project_id', 'experts', ['project_id'])

    # 5. Transcripts
    op.create_table(
        'transcripts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('expert_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('experts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('file_name', sa.String(length=500), nullable=False),
        sa.Column('file_path', sa.String(length=1000), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='uploaded'),
        sa.Column('duration', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_transcripts_project_id', 'transcripts', ['project_id'])
    op.create_index('ix_transcripts_expert_id', 'transcripts', ['expert_id'])

    # 6. Utterances
    op.create_table(
        'utterances',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('transcript_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('transcripts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('expert_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('experts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('speaker', sa.String(length=255), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('timestamp_start', sa.String(length=20), nullable=True),
        sa.Column('timestamp_end', sa.String(length=20), nullable=True),
        sa.Column('sequence', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_utterances_transcript_id', 'utterances', ['transcript_id'])
    op.create_index('ix_utterances_expert_id', 'utterances', ['expert_id'])
    op.create_index('ix_utterances_sequence', 'utterances', ['transcript_id', 'sequence'])

    # 7. Evidence
    op.create_table(
        'evidence',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('question_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('research_questions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('transcript_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('transcripts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('expert_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('experts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('utterance_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('utterances.id', ondelete='CASCADE'), nullable=False),
        sa.Column('quote', sa.Text(), nullable=False),
        sa.Column('topic', sa.String(length=500), nullable=True),
        sa.Column('relevance_score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_evidence_project_id', 'evidence', ['project_id'])
    op.create_index('ix_evidence_question_id', 'evidence', ['question_id'])
    op.create_index('ix_evidence_expert_id', 'evidence', ['expert_id'])
    op.create_index('ix_evidence_transcript_id', 'evidence', ['transcript_id'])
    op.create_index('ix_evidence_utterance_id', 'evidence', ['utterance_id'])

    # 8. Answers
    op.create_table(
        'answers',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('question_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('research_questions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('expert_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('experts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('answer_text', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_answers_project_id', 'answers', ['project_id'])
    op.create_index('ix_answers_question_id', 'answers', ['question_id'])
    op.create_index('ix_answers_expert_id', 'answers', ['expert_id'])

    # 9. Answer <-> Evidence association table
    op.create_table(
        'answer_evidence',
        sa.Column('answer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('answers.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('evidence_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('evidence.id', ondelete='CASCADE'), primary_key=True),
    )

    # 10. Differences
    op.create_table(
        'differences',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('question_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('research_questions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_differences_project_id', 'differences', ['project_id'])
    op.create_index('ix_differences_question_id', 'differences', ['question_id'])

    # 11. Difference Perspectives
    op.create_table(
        'difference_perspectives',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('difference_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('differences.id', ondelete='CASCADE'), nullable=False),
        sa.Column('expert_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('experts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('perspective', sa.Text(), nullable=False),
    )
    op.create_index('ix_difference_perspectives_difference_id', 'difference_perspectives', ['difference_id'])

    # 12. Difference <-> Evidence association table
    op.create_table(
        'difference_evidence',
        sa.Column('difference_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('differences.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('evidence_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('evidence.id', ondelete='CASCADE'), primary_key=True),
    )

    # 13. Insights
    op.create_table(
        'insights',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('question_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('research_questions.id', ondelete='SET NULL'), nullable=True),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_insights_project_id', 'insights', ['project_id'])
    op.create_index('ix_insights_question_id', 'insights', ['question_id'])

    # 14. Insight <-> Evidence association table
    op.create_table(
        'insight_evidence',
        sa.Column('insight_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('insights.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('evidence_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('evidence.id', ondelete='CASCADE'), primary_key=True),
    )


def downgrade() -> None:
    op.drop_table('insight_evidence')
    op.drop_table('insights')
    op.drop_table('difference_evidence')
    op.drop_table('difference_perspectives')
    op.drop_table('differences')
    op.drop_table('answer_evidence')
    op.drop_table('answers')
    op.drop_table('evidence')
    op.drop_table('utterances')
    op.drop_table('transcripts')
    op.drop_table('experts')
    op.drop_table('research_questions')
    op.drop_table('interview_guides')
    op.drop_table('projects')

-- Enable Row Level Security (RLS) on all public tables
-- This fixes the security vulnerabilities identified in Supabase dashboard

-- Enable RLS on all tables
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.workflow_executions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.teams ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.team_invites ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.shared_workflows ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.collaboration_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.collaboration_messages ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for users table
CREATE POLICY "Users can view own profile" ON public.users
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON public.users
  FOR UPDATE USING (auth.uid() = id);

-- Create RLS policies for chat_sessions table
CREATE POLICY "Users can view own chat sessions" ON public.chat_sessions
  FOR ALL USING (auth.uid() = user_id);

-- Create RLS policies for chat_messages table
CREATE POLICY "Users can view messages from own chat sessions" ON public.chat_messages
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM public.chat_sessions 
      WHERE id = chat_messages.session_id 
      AND user_id = auth.uid()
    )
  );

CREATE POLICY "Users can insert messages to own chat sessions" ON public.chat_messages
  FOR INSERT WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.chat_sessions 
      WHERE id = chat_messages.session_id 
      AND user_id = auth.uid()
    )
  );

-- Create RLS policies for workflow_executions table
CREATE POLICY "Users can view own workflow executions" ON public.workflow_executions
  FOR ALL USING (auth.uid() = user_id);

-- Create RLS policies for teams table
CREATE POLICY "Users can view teams they belong to" ON public.teams
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM public.team_members 
      WHERE team_id = teams.id 
      AND user_id = auth.uid()
    )
  );

CREATE POLICY "Team owners can update teams" ON public.teams
  FOR UPDATE USING (auth.uid() = owner_id);

CREATE POLICY "Authenticated users can create teams" ON public.teams
  FOR INSERT WITH CHECK (auth.uid() = owner_id);

-- Create RLS policies for team_invites table
CREATE POLICY "Users can view invites sent to them" ON public.team_invites
  FOR SELECT USING (auth.uid() = invited_user_id);

CREATE POLICY "Team owners can manage invites for their teams" ON public.team_invites
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM public.teams 
      WHERE id = team_invites.team_id 
      AND owner_id = auth.uid()
    )
  );

-- Create RLS policies for shared_workflows table
CREATE POLICY "Users can view workflows shared with them" ON public.shared_workflows
  FOR SELECT USING (
    auth.uid() = shared_with_user_id OR
    EXISTS (
      SELECT 1 FROM public.workflow_executions 
      WHERE id = shared_workflows.workflow_id 
      AND user_id = auth.uid()
    )
  );

CREATE POLICY "Workflow owners can share their workflows" ON public.shared_workflows
  FOR INSERT WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.workflow_executions 
      WHERE id = shared_workflows.workflow_id 
      AND user_id = auth.uid()
    )
  );

-- Create RLS policies for collaboration_sessions table
CREATE POLICY "Users can view collaboration sessions they participate in" ON public.collaboration_sessions
  FOR SELECT USING (
    auth.uid() = created_by OR
    EXISTS (
      SELECT 1 FROM public.collaboration_participants 
      WHERE session_id = collaboration_sessions.id 
      AND user_id = auth.uid()
    )
  );

CREATE POLICY "Authenticated users can create collaboration sessions" ON public.collaboration_sessions
  FOR INSERT WITH CHECK (auth.uid() = created_by);

CREATE POLICY "Session creators can update sessions" ON public.collaboration_sessions
  FOR UPDATE USING (auth.uid() = created_by);

-- Create RLS policies for collaboration_messages table
CREATE POLICY "Users can view messages from sessions they participate in" ON public.collaboration_messages
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM public.collaboration_sessions cs
      WHERE cs.id = collaboration_messages.session_id 
      AND (
        cs.created_by = auth.uid() OR
        EXISTS (
          SELECT 1 FROM public.collaboration_participants cp
          WHERE cp.session_id = cs.id 
          AND cp.user_id = auth.uid()
        )
      )
    )
  );

CREATE POLICY "Users can send messages to sessions they participate in" ON public.collaboration_messages
  FOR INSERT WITH CHECK (
    auth.uid() = user_id AND
    EXISTS (
      SELECT 1 FROM public.collaboration_sessions cs
      WHERE cs.id = collaboration_messages.session_id 
      AND (
        cs.created_by = auth.uid() OR
        EXISTS (
          SELECT 1 FROM public.collaboration_participants cp
          WHERE cp.session_id = cs.id 
          AND cp.user_id = auth.uid()
        )
      )
    )
  );

-- Grant necessary permissions to authenticated users
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;
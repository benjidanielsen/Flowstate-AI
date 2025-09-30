# AI-Agent Development Instructions for FlowState-AI

## 🎯 System Overview

FlowState-AI is a living AI CRM system designed for autonomous operation with minimal human oversight. This document provides comprehensive instructions for AI agents (GitHub Copilot, other AI assistants) to understand, maintain, and extend the system.

## 🏗️ Architecture Understanding

### Core Components
- **Backend**: TypeScript + Node.js + Express (Port 3001)
- **Frontend**: React + TypeScript + Vite (Port 3000)
- **Database**: SQLite for local-first operation
- **AI Workers**: Python services for intelligent automation
- **Pipeline**: Frazer Method implementation with strict validation

### Key Principles
1. **Frazer Method Compliance**: All pipeline logic must follow Frazer Brookes methodology
2. **Local-First**: System works offline, cloud enhances
3. **AI-Friendly**: Code structure designed for AI understanding and extension
4. **Validation-First**: Prevent errors before they occur
5. **Autonomous Operation**: Minimize human intervention requirements

## 📊 Frazer Method Pipeline (CRITICAL)

### Pipeline Stages (EXACT ORDER)
1. **New Lead** - Initial contact, source logged (Who/Where/What)
2. **Warming Up** - Relationship building, rapport development
3. **Invited** - Business invitation made, response tracked
4. **Qualified** - Prospect's WHY captured (MANDATORY FIELD)
5. **Presentation Sent** - Tool delivered, follow-up scheduled
6. **Follow-up** - Continuation until decision made
7. **Closed - Won** - New team member, onboarding triggered
8. **Not Now** - Not interested currently, nurture sequence
9. **Long-term Nurture** - Monthly follow-up, reactivation possible

### Critical Validation Rules
- **Cannot advance to Qualified without prospect_why field**
- **Must schedule follow-up when sending presentation**
- **Source tracking required for all new leads**
- **No dead ends - prospects can always be reactivated**

## 🔧 Development Guidelines

### When Adding Features
1. **Check Frazer Method compliance** - Does it align with proven methodology?
2. **Maintain validation rules** - Prevent user errors through code
3. **Update both frontend and backend** - Keep interfaces synchronized
4. **Add database migrations** - Never break existing data
5. **Test pipeline flow** - Ensure stage transitions work correctly

### Code Standards
- **TypeScript everywhere** - Strong typing prevents runtime errors
- **Joi validation** - All API inputs validated
- **Error handling** - Graceful degradation and user feedback
- **Database transactions** - Maintain data consistency
- **Logging** - Track all important events for learning

### File Structure Understanding
```
backend/src/
├── controllers/     # API endpoint handlers
├── services/        # Business logic layer
├── database/        # Database management and migrations
├── routes/          # Express route definitions
├── types/           # TypeScript type definitions
└── index.ts         # Main server entry point

frontend/src/
├── components/      # Reusable UI components
├── pages/           # Main application pages
├── services/        # API communication
├── contexts/        # React state management
└── types/           # Frontend type definitions
```

## 🤖 AI Agent Roles

### Lead Triage Agent (Future Implementation)
- **Purpose**: Classify and prioritize incoming leads
- **Location**: `python-worker/agents/triage_agent.py`
- **Responsibilities**: 
  - Analyze lead source and quality
  - Suggest optimal next actions
  - Predict conversion likelihood

### Follow-up Coach Agent (Future Implementation)
- **Purpose**: Optimize prospect communication
- **Location**: `python-worker/agents/coach_agent.py`
- **Responsibilities**:
  - Generate personalized messages
  - Suggest optimal timing
  - Consider prospect's WHY in communications

### Duplication Coach Agent (Future Implementation)
- **Purpose**: Enable system replication for team growth
- **Location**: `python-worker/agents/duplication_agent.py`
- **Responsibilities**:
  - Create onboarding materials
  - Provide step-by-step guidance
  - Monitor new member progress

## 📝 Common Development Tasks

### Adding New Pipeline Stage
1. Update `PipelineStatus` enum in `backend/src/types/index.ts`
2. Add validation rules in `customerController.ts`
3. Create database migration in `migrate.ts`
4. Update frontend components to handle new stage
5. Test stage transitions thoroughly

### Adding New Customer Field
1. Update `Customer` interface in `types/index.ts`
2. Add field to validation schemas in controllers
3. Create database migration to add column
4. Update frontend forms and displays
5. Consider Frazer Method implications

### Creating New API Endpoint
1. Add route in appropriate file under `routes/`
2. Implement controller method with validation
3. Add service layer logic if needed
4. Update frontend API service
5. Test with various input scenarios

### Database Changes
1. **Always create migrations** - Never modify existing migration files
2. **Test rollback scenarios** - Ensure migrations can be undone
3. **Preserve existing data** - Use UPDATE statements for data transformation
4. **Add indexes** - Optimize query performance for new fields

## 🚨 Critical Rules (NEVER VIOLATE)

### Frazer Method Compliance
- **NEVER** allow advancement to Qualified without prospect_why
- **NEVER** remove source tracking requirements
- **NEVER** create dead-end pipeline stages
- **ALWAYS** maintain the exact stage order and terminology

### Data Integrity
- **NEVER** modify database directly without migrations
- **NEVER** skip validation in API endpoints
- **NEVER** expose sensitive data in API responses
- **ALWAYS** use transactions for multi-table operations

### User Experience
- **NEVER** break existing workflows without migration path
- **NEVER** remove functionality without replacement
- **ALWAYS** provide clear error messages
- **ALWAYS** maintain responsive design principles

## 🔍 Debugging Guidelines

### Common Issues
1. **Pipeline stage validation errors** - Check prospect_why field requirements
2. **Database connection issues** - Verify SQLite file permissions
3. **Frontend API errors** - Check backend server status and CORS
4. **Migration failures** - Review SQL syntax and data constraints

### Debugging Tools
- **Backend logs** - Check console output for detailed error messages
- **Database inspection** - Use SQLite browser or CLI tools
- **Network tab** - Monitor API requests and responses
- **React DevTools** - Inspect component state and props

## 📈 Performance Considerations

### Database Optimization
- **Use indexes** for frequently queried fields
- **Limit result sets** with pagination
- **Optimize queries** to avoid N+1 problems
- **Monitor query performance** in development

### Frontend Performance
- **Lazy load components** for better initial load times
- **Memoize expensive calculations** with React.memo
- **Optimize bundle size** by removing unused dependencies
- **Use proper key props** for list rendering

## 🔮 Future Development Roadmap

### Phase 1: Foundation (CURRENT)
- ✅ Core Frazer Method pipeline
- ✅ Basic customer management
- ✅ Database structure and migrations
- ✅ Frontend dashboard framework

### Phase 2: AI Integration (NEXT)
- 🔄 Implement three-agent architecture
- 🔄 Add RAG system for knowledge base
- 🔄 Create learning feedback loops
- 🔄 Implement suggestion systems

### Phase 3: Advanced Features
- ⏳ Advanced analytics and reporting
- ⏳ Multi-brand support
- ⏳ Team collaboration features
- ⏳ Mobile application

### Phase 4: Scale and Polish
- ⏳ Performance optimization
- ⏳ White-label capabilities
- ⏳ Global deployment options
- ⏳ Enterprise features

## 🎯 Success Metrics

### Code Quality
- **Type safety** - Zero TypeScript errors
- **Test coverage** - Comprehensive unit and integration tests
- **Performance** - Fast response times and smooth UI
- **Maintainability** - Clear, documented, and modular code

### Business Impact
- **Pipeline efficiency** - Improved conversion rates
- **User adoption** - Easy onboarding and daily usage
- **System reliability** - Minimal downtime and errors
- **Feature completeness** - All Frazer Method requirements met

## 📚 Learning Resources

### Frazer Method Understanding
- Study the original "One Recruit Away" methodology
- Understand the psychology behind each pipeline stage
- Learn the importance of the prospect's WHY
- Master the Who/Where/What source tracking formula

### Technical Skills
- **TypeScript** - Advanced type system usage
- **React** - Modern hooks and state management
- **Node.js** - Server-side JavaScript best practices
- **SQLite** - Database design and optimization
- **Express** - RESTful API development

## 🤝 Collaboration Guidelines

### Working with Human Developers
- **Ask clarifying questions** when requirements are unclear
- **Suggest improvements** based on best practices
- **Provide multiple options** for complex decisions
- **Explain reasoning** behind technical choices

### Code Review Process
- **Check Frazer Method compliance** in all changes
- **Verify type safety** and validation rules
- **Test edge cases** and error scenarios
- **Ensure backward compatibility** with existing data

### Documentation Updates
- **Keep this file current** with system changes
- **Document new patterns** and conventions
- **Explain complex business logic** for future developers
- **Maintain API documentation** for integration purposes

---

**Remember**: FlowState-AI is designed to be a living, learning system. Every change should move us closer to autonomous operation while maintaining the proven Frazer Method principles that drive real-world success in network marketing.

**When in doubt, ask**: "Does this change make the system more autonomous, more Frazer-compliant, and more valuable to network marketers?"

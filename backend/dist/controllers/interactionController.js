"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.InteractionController = void 0;
const interactionService_1 = require("../services/interactionService");
class InteractionController {
    constructor() {
        this.getInteractionsByCustomer = async (req, res) => {
            try {
                const { customerId } = req.params;
                const interactions = await this.interactionService.getInteractionsByCustomer(customerId);
                res.json(interactions);
            }
            catch (error) {
                console.error('Error fetching interactions:', error);
                res.status(500).json({ error: 'Internal server error' });
            }
        };
        this.createInteraction = async (req, res) => {
            try {
                const interactionData = req.body;
                if (!interactionData.customer_id || !interactionData.type || !interactionData.content) {
                    return res.status(400).json({ error: 'customer_id, type, and content are required' });
                }
                const interaction = await this.interactionService.createInteraction(interactionData);
                res.status(201).json(interaction);
            }
            catch (error) {
                console.error('Error creating interaction:', error);
                res.status(500).json({ error: 'Internal server error' });
            }
        };
        this.updateInteraction = async (req, res) => {
            try {
                const { id } = req.params;
                const updates = req.body;
                const interaction = await this.interactionService.updateInteraction(id, updates);
                if (!interaction) {
                    return res.status(404).json({ error: 'Interaction not found' });
                }
                res.json(interaction);
            }
            catch (error) {
                console.error('Error updating interaction:', error);
                res.status(500).json({ error: 'Internal server error' });
            }
        };
        this.deleteInteraction = async (req, res) => {
            try {
                const { id } = req.params;
                const deleted = await this.interactionService.deleteInteraction(id);
                if (!deleted) {
                    return res.status(404).json({ error: 'Interaction not found' });
                }
                res.status(204).send();
            }
            catch (error) {
                console.error('Error deleting interaction:', error);
                res.status(500).json({ error: 'Internal server error' });
            }
        };
        this.getUpcomingInteractions = async (req, res) => {
            try {
                const limit = parseInt(req.query.limit) || 20;
                const interactions = await this.interactionService.getUpcomingInteractions(limit);
                res.json(interactions);
            }
            catch (error) {
                console.error('Error fetching upcoming interactions:', error);
                res.status(500).json({ error: 'Internal server error' });
            }
        };
        this.interactionService = new interactionService_1.InteractionService();
    }
}
exports.InteractionController = InteractionController;
//# sourceMappingURL=interactionController.js.map
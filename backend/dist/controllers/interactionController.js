"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.interactionController = void 0;
const interactionService_1 = require("../services/interactionService");
exports.interactionController = {
    async createInteraction(req, res) {
        try {
            const { customer_id, type, summary, notes, interaction_date } = req.body;
            const newInteraction = await interactionService_1.interactionService.create({
                customer_id,
                type,
                summary,
                notes,
                interaction_date: interaction_date ? new Date(interaction_date) : new Date(),
            });
            res.status(201).json(newInteraction);
        }
        catch (error) {
            console.error("Error creating interaction:", error);
            res.status(500).json({ message: "Error creating interaction" });
        }
    },
    async getInteractionsByCustomerId(req, res) {
        try {
            const { customerId } = req.params;
            const interactions = await interactionService_1.interactionService.getByCustomerId(customerId);
            res.status(200).json(interactions);
        }
        catch (error) {
            console.error("Error fetching interactions:", error);
            res.status(500).json({ message: "Error fetching interactions" });
        }
    },
    async getInteractionById(req, res) {
        try {
            const { id } = req.params;
            const interaction = await interactionService_1.interactionService.getById(id);
            if (interaction) {
                res.status(200).json(interaction);
            }
            else {
                res.status(404).json({ message: "Interaction not found" });
            }
        }
        catch (error) {
            console.error("Error fetching interaction:", error);
            res.status(500).json({ message: "Error fetching interaction" });
        }
    },
    async updateInteraction(req, res) {
        try {
            const { id } = req.params;
            const updates = req.body;
            const updatedInteraction = await interactionService_1.interactionService.update(id, updates);
            if (updatedInteraction) {
                res.status(200).json(updatedInteraction);
            }
            else {
                res.status(404).json({ message: "Interaction not found" });
            }
        }
        catch (error) {
            console.error("Error updating interaction:", error);
            res.status(500).json({ message: "Error updating interaction" });
        }
    },
    async deleteInteraction(req, res) {
        try {
            const { id } = req.params;
            await interactionService_1.interactionService.delete(id);
            res.status(204).send();
        }
        catch (error) {
            console.error("Error deleting interaction:", error);
            res.status(500).json({ message: "Error deleting interaction" });
        }
    },
};
//# sourceMappingURL=interactionController.js.map
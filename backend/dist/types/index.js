"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ReminderType = exports.InteractionType = exports.PipelineStatus = void 0;
var PipelineStatus;
(function (PipelineStatus) {
    PipelineStatus["NEW_LEAD"] = "New Lead";
    PipelineStatus["WARMING_UP"] = "Warming Up";
    PipelineStatus["INVITED"] = "Invited";
    PipelineStatus["QUALIFIED"] = "Qualified";
    PipelineStatus["PRESENTATION_SENT"] = "Presentation Sent";
    PipelineStatus["FOLLOW_UP"] = "Follow-up";
    PipelineStatus["CLOSED_WON"] = "Closed - Won";
    PipelineStatus["NOT_NOW"] = "Not Now";
    PipelineStatus["LONG_TERM_NURTURE"] = "Long-term Nurture";
})(PipelineStatus || (exports.PipelineStatus = PipelineStatus = {}));
var InteractionType;
(function (InteractionType) {
    InteractionType["NOTE"] = "note";
    InteractionType["CALL"] = "call";
    InteractionType["EMAIL"] = "email";
    InteractionType["MEETING"] = "meeting";
    InteractionType["REMINDER"] = "reminder";
})(InteractionType || (exports.InteractionType = InteractionType = {}));
var ReminderType;
(function (ReminderType) {
    ReminderType["FOLLOW_UP_24H"] = "follow_up_24h";
    ReminderType["FOLLOW_UP_48H"] = "follow_up_48h";
    ReminderType["FOLLOW_UP_2H"] = "follow_up_2h";
    ReminderType["FOLLOW_UP_1D"] = "follow_up_1d";
    ReminderType["FOLLOW_UP_7D"] = "follow_up_7d";
    ReminderType["FOLLOW_UP"] = "follow_up";
})(ReminderType || (exports.ReminderType = ReminderType = {}));
//# sourceMappingURL=index.js.map
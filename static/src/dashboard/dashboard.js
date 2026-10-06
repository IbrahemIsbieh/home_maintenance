/** @odoo-module */
import { registry } from "@web/core/registry";
import { Component, onWillStart, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class HomeMaintenanceDashboard extends Component {
    static template = "home_maintenance.Dashboard";
    static props = ["*"];

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");

        this.states = [
            { key: "new", label: "New", color: "secondary" },
            { key: "scheduled", label: "Scheduled", color: "info" },
            { key: "in_progress", label: "In Progress", color: "warning" },
            { key: "done", label: "Done", color: "success" },
            { key: "cancelled", label: "Cancelled", color: "danger" },
        ];
        this.urgentDomain = [
            ["priority", "=", "3"],
            ["state", "not in", ["done", "cancelled"]],
        ];

        this.state = useState({
            counts: {},
            urgent: 0,
            visits: [],
        });

        onWillStart(async () => {
            await this.loadData();
        });
    }

    async loadData() {
        const counts = await Promise.all(
            this.states.map((s) =>
                this.orm.searchCount("home.request", [["state", "=", s.key]])
            )
        );
        this.states.forEach((s, i) => {
            this.state.counts[s.key] = counts[i];
        });

        this.state.urgent = await this.orm.searchCount(
            "home.request",
            this.urgentDomain
        );

        try {
            this.state.visits = await this.orm.searchRead(
                "home.visit",
                [["state", "=", "planned"]],
                ["request_id", "technician_id", "visit_date"],
                { limit: 5, order: "visit_date asc" }
            );
        } catch (e) {
            // المستخدم ما عنده صلاحية على الزيارات (مثلاً دور User)
            this.state.visits = [];
        }
    }

    openRequests(stateKey, label) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: label + " Requests",
            res_model: "home.request",
            views: [[false, "list"], [false, "form"]],
            domain: [["state", "=", stateKey]],
        });
    }
    openUrgent() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Urgent Requests",
            res_model: "home.request",
            views: [[false, "list"], [false, "form"]],
            domain: this.urgentDomain,
        });
    }


}

registry.category("actions").add("home_maintenance.dashboard", HomeMaintenanceDashboard);
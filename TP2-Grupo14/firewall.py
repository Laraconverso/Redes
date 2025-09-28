from pox.core import core
from pox.lib.revent import EventMixin
from pox.lib.util import dpidToStr
import json
from flow_builder import FlowBuilder

log = core.getLogger()


class Firewall(EventMixin):
    def __init__(self, target_switches=None):
        self.listenTo(core.openflow)
        if target_switches is None:
            log.debug("Enabling Firewall Module for all switches")
            self.target_switches = None
        else:
            try:
                self.target_switches = parse_target_switches(target_switches)
                log.debug("Enabling Firewall Module for switches: %s", sorted(self.target_switches))
            except ValueError as e:
                log.error("Invalid switch list format: %s. Expected comma-separated integers (e.g., '1,3')", target_switches)
                return

        self.rules = self.load_rules("rules.json")

    def load_rules(self, filename):
        """Load firewall rules from JSON file"""
        try:
            with open(filename) as file:
                rules = json.load(file)
            log.debug("Loaded %d firewall rules", len(rules.get('reglas', [])))
            return rules
        except FileNotFoundError:
            log.warning("Rules file %s not found. Using empty ruleset.", filename)
            return {"reglas": []}
        except json.JSONDecodeError as e:
            log.error("Error parsing rules file: %s", e)
            return {"reglas": []}

    def _handle_ConnectionUp(self, event):
        """Handle switch connection and install firewall rules"""
        log.debug("Connection Up from %s", dpidToStr(event.dpid))

        # Install on specified switches (all by default)
        if self.target_switches is None or event.dpid in self.target_switches:
            log.info("Installing firewall rules on switch %s", dpidToStr(event.dpid))
            self.install_firewall_rules(event)
        else:
            log.debug("Skipping firewall installation on switch %s", dpidToStr(event.dpid))

    def install_firewall_rules(self, event):
        """Install blocking flow rules on the switch based on firewall configuration"""
        if not self.rules.get('reglas'):
            log.debug("No firewall rules defined")
            return

        for rule in self.rules['reglas']:
            self.install_blocking_rule(event, rule)

        log.info("Firewall rules installed on switch %s", dpidToStr(event.dpid))

    def install_blocking_rule(self, event, rule):
        """Install a single blocking rule on the switch"""
        try:
            msg = FlowBuilder.build_blocking_flow(rule)
            event.connection.send(msg)

            rule_name = rule.get('name', 'unnamed')
            log.debug("Installed blocking rule '%s' on switch %s", rule_name, dpidToStr(event.dpid))

        except Exception as e:
            log.error("Error installing rule %s: %s", rule.get('name', 'unnamed'), str(e))


def parse_target_switches(target_switches):
    """
    Parse target switches parameter into a set of switch IDs

    Args:
        target_switches: Comma-separated string (e.g., "1,3") or None for all switches

    Returns:
        set: Set of switch IDs, or None if target_switches is None

    Raises:
        ValueError: If the format is invalid
    """
    if target_switches is None:
        return None

    # Parse comma-separated string
    switch_list = [int(s.strip()) for s in target_switches.split(',')]
    return set(switch_list)

def launch(target_switches=None):
    log.debug("Launching firewall")
    core.registerNew(Firewall, target_switches)

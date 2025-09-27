from hyperon import MeTTa, E, S, ValueAtom
import random

def initialize_banker_knowledge(metta: MeTTa):
    """Initialize the MeTTa knowledge graph with banker game rules and negotiation strategies."""
    
    # Round-based house edge multipliers
    metta.space().add_atom(E(S("house_edge"), S("early_round"), ValueAtom(0.65)))  # rounds 1-2
    metta.space().add_atom(E(S("house_edge"), S("mid_round"), ValueAtom(0.75)))   # rounds 3-4
    metta.space().add_atom(E(S("house_edge"), S("late_round"), ValueAtom(0.85)))  # rounds 5+
    
    # Sentiment-based offer adjustments
    metta.space().add_atom(E(S("sentiment_multiplier"), S("confident"), ValueAtom(1.05)))
    metta.space().add_atom(E(S("sentiment_multiplier"), S("desperate"), ValueAtom(0.95)))
    metta.space().add_atom(E(S("sentiment_multiplier"), S("neutral"), ValueAtom(1.0)))
    metta.space().add_atom(E(S("sentiment_multiplier"), S("aggressive"), ValueAtom(0.90)))
    
    # Risk tolerance adjustments based on remaining cards
    metta.space().add_atom(E(S("risk_adjustment"), S("high_variance"), ValueAtom(0.90)))  # when big cards remain
    metta.space().add_atom(E(S("risk_adjustment"), S("low_variance"), ValueAtom(1.05)))   # when mostly small cards
    metta.space().add_atom(E(S("risk_adjustment"), S("medium_variance"), ValueAtom(1.0)))
    
    # Psychological pressure tactics
    metta.space().add_atom(E(S("pressure_tactic"), S("early_game"), ValueAtom("tease about big cards ahead")))
    metta.space().add_atom(E(S("pressure_tactic"), S("mid_game"), ValueAtom("emphasize risk of losing everything")))
    metta.space().add_atom(E(S("pressure_tactic"), S("late_game"), ValueAtom("highlight guaranteed money vs risk")))
    
    # Offer presentation styles
    metta.space().add_atom(E(S("presentation_style"), S("confident_player"), ValueAtom("playful and challenging")))
    metta.space().add_atom(E(S("presentation_style"), S("desperate_player"), ValueAtom("cold and calculating")))
    metta.space().add_atom(E(S("presentation_style"), S("neutral_player"), ValueAtom("professional and persuasive")))
    
    # Game state tracking
    metta.space().add_atom(E(S("game_state"), S("round"), ValueAtom(1)))
    metta.space().add_atom(E(S("game_state"), S("total_offers"), ValueAtom(0)))
    metta.space().add_atom(E(S("game_state"), S("accepted_offers"), ValueAtom(0)))
    
    # Banker personality traits
    metta.space().add_atom(E(S("personality"), S("base_tone"), ValueAtom("witty and shrewd")))
    metta.space().add_atom(E(S("personality"), S("negotiation_style"), ValueAtom("psychological pressure")))
    metta.space().add_atom(E(S("personality"), S("risk_communication"), ValueAtom("emphasize downside")))
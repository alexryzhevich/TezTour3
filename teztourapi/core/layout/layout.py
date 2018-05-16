from core.config import initial_grid as init_config, layout as layout_config, parameters as param_config


class Layout:

    def __init__(self, name, data, date_relations, out_of_order, update_date, no_losses, width=layout_config.MIN_WIDTH,
                 min_days=param_config.MIN_DAYS, max_days=param_config.MAX_DAYS,
                 duration_limit=param_config.DURATION_LIMIT, relations=param_config.RELATIONS, id=None):
        self.name = name
        self.data = data
        self.date_relations = date_relations
        self.out_of_order = out_of_order
        self.update_date = update_date
        self.no_losses = no_losses
        self.width = width
        self.min_days = min_days
        self.max_days = max_days
        self.duration_limit = duration_limit
        self.relations = relations
        self.id = id

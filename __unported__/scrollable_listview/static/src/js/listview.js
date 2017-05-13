openerp.scrollable_listview = function (instance) {

    instance.scrollable_listview = {
        preventFOUC: function(self, time_slice, callback){
            /*
             * this function potentially is called multiple times in succession
             * to avoid flickering, we only call it the last time
             *
             *  Extract this method from Stefan Rijnhart scrollable_listview_x2m module
             */
            var now = (new Date()).getTime();
            self.fouc_callback = callback;
            if(!self.fouc_timer ||
               self.fouc_timer + time_slice > now)
            {
                self.fouc_timer = now;
                setTimeout(function()
                {
                    if(self.fouc_timer == now)
                    {
                        self.fouc_callback();
                    }
                },
                time_slice);
                return;
            }
            this.fouc_timer = now;
        }
    };

    instance.web.ListView.include({
        listview_ref: '',
        is_tree_view: false,
        is_multiheader: false,
        resized_column: null,
        columns_width: {},
        initial_cursor_position_x: 0,
        DEFAULT_COLUMN_WIDTH: {
            'oe_list_header_char': 200,
            'oe_list_header_binary': 200,
            'oe_list_header_datetime': 60,
            'oe_list_header_many2one': 150,
            'oe_list_header_reference': 125,
            'oe_list_header_date': 60,
            'oe_list_header_float': 75,
            'oe_list_header_integer': 75,
            'oe_list_header_decimal': 75,
            'oe_list_header_color': 125,
            'oe_list_header_selection': 80,
            'oe_list_header_group': 50,
            'oe_list_header_boolean': 50,
            'oe_list_header_boolean_switch': 50,
            'oe_list_header_selector': 15,
            'oe_list_header_handle': 10,
            'oe_list_header_action': 15,
            'oe_list_header_object': 15,
            'oe_list_header_delete': 15,
        },
        selector: '.openerp .scrollable_listview table.oe_list_content ',
        style: null,
        start: function() {
            var r = this._super();
            // Event find by reading Stefan Rijnhart scrollable_listview_x2m module
            instance.web.bus.on('resize', this, this.manage_views);
            var isPopup = false;
            if(this.$el.parent()){
                isPopup = this.$el.parent().hasClass("oe_popup_list");
            }
            var isDashboard = false;
            if(window.$('.oe_dashboard .oe_action').length > 0){
                isDashboard = true;
            }
            // what about this.$el.viewmanager.active_view ?
            if(this.getParent().action && (this.view_type == 'tree' ||
               this.view_type == 'list_multiheader') &&
               !isPopup && !isDashboard){
                if (this.view_type == 'list_multiheader'){
                    this.is_multiheader = true;
                }
                this.is_tree_view = true;
                this.$el.addClass('scrollable_listview');
                this.columns_width = {};
                this.listview_ref = this.model + '-' + this.getParent().action.id;
                if(typeof localStorage!='undefined') {
                    var columns = localStorage.getItem(this.listview_ref);
                    if(columns){
                        this.columns_width = JSON.parse(columns);
                    }
                }
            }
            return r;
        },
        load_list: function(data) {
            this._super(data);
            if(this.is_tree_view){
                var table = this.$el.find("table");
                table.scroll(this.scrolling);
                table.on("mousewheel", this, this.beforescroll);
                this.on('edit:before', this, this.disable_scroll_bar);
                this.on('save:after', this, this.enable_scroll_bar);
                this.on('cancel:after', this, this.enable_scroll_bar);
                this.$el.find("th").on('mousedown', this,
                                       this.start_resizing_column);
            }
        },
        sort_by_column: function(event){
            event.stopPropagation();
            if(event.target.tagName != 'TH'){
                this._super(event);
            }
        },
        start_resizing_column: function(event){
            event.stopPropagation();
            if(event.target.tagName === 'TH'){
                var self = event.data;
                if(self.is_multiheader &&
                   !$(event.currentTarget).hasClass('oe_multiheader-field')){
                    // disable resizing main header
                    return;
                }
                self.resized_column = $(event.currentTarget);
                self.initial_cursor_position_x = event.pageX - $(event.currentTarget).width();
                $(window).on('mousemove', self, self.resizing_column);
                $(window).on('mouseup', self, self.stop_resizing_column);
            }
        },
        resizing_column: function(event){
            event.stopPropagation();
            self = event.data;
            var new_width = event.pageX - self.initial_cursor_position_x;
            if(new_width > 0){
                self.resized_column.
                    css('width', event.pageX - self.initial_cursor_position_x);
                self.resized_column.
                    css('min-width', event.pageX - self.initial_cursor_position_x);
                self.resized_column.
                    css('max-width', event.pageX - self.initial_cursor_position_x);
            }
        },
        stop_resizing_column: function(event){
            event.stopPropagation();
            event.stopPropagation();
            var self = event.data;
            var column_id = self.get_column_id(self.resized_column);
            if(self.resized_column){
                self.columns_width[column_id] = self.resized_column.width();
                self.save_column_width();
            }
            $(window).off('mouseup', this.stop_resizing_column);
            $(window).off('mousemove', this.resizing_column);
            self.resized_column = null;
            self.initial_cursor_position_x = 0;
            self.manage_views();
        },
        reload_content: function(){
            var self = this;
            return this._super().then( function (){
                self.manage_views();
            });
        },
        save_column_width: function(){
            if(typeof localStorage!='undefined') {
                localStorage.setItem(self.listview_ref,
                                     JSON.stringify(self.columns_width));
            }
        },
        destroy: function(){
            var table = this.$el.find("table");
            table.unbind('scroll', this.scrolling);
            table.off("mousewheel", this, this.beforescroll);
            // Event find by reading Stefan Rijnhart scrollable_listview_x2m module
            instance.web.bus.off('resize', this, this.manage_views);
            this.removeStyle(this.style);
            this._super();
        },
        manage_views: function(){
            if(this.is_tree_view){

                instance.scrollable_listview.preventFOUC(
                    this, 100, this.manage_views);

                var table = this.$el.find("table");
                this.style = this.initStyle(this.style);
                this.manage_column_width();
                this.manage_listview_height();
            }
        },
        do_add_record: function () {
            this.$el.find('table').scrollTop(0);
            this._super();
        },
        editable: function () {
            //force to edit on the top
            return !this.grouped &&
                !this.options.disable_editable_mode &&
                (this.fields_view.arch.attrs.editable ? 'top' : false ||
                 this._context_editable || this.options.editable);
        },
        enable_scroll_bar: function(event, data){
            this.$el.find('table.oe_list_content').removeClass('noscroll');
        },
        disable_scroll_bar: function(event, data){
            this.$el.find('table.oe_list_content').addClass('noscroll');
        },
        beforescroll: function(event, data){
            if(event.data.editor.is_editing()){
                event.data.preventDefault(event);
            }
        },
        scrolling: function(event){
            var thead = $(this).find("thead");
            if (this.scrollTop > 0){
                thead.addClass('scrolling');
            }else{
                thead.removeClass('scrolling');
            }
        },
        preventDefault: function (e) {
            e = e || window.event;
            if (e.preventDefault)
                e.preventDefault();
            e.returnValue = false;
        },
        manage_column_width: function(){
            var header = this.$el.find('table > thead');
            var last_row_header = header.find('tr:last-child');
            if (last_row_header && last_row_header.children().length > 0){
                var head_cells = last_row_header.children();
                var rules = [];
                var index = 1;
                var offset_row = 0;
                if (this.is_multiheader){
                    offset_row = 1; //the multi header module add a white row!
                }
                var header_rows = header.find('tr');
                var row_count = header_rows.length;
                var level_field_position = [];
                var self = this;
                col_with_calculation = function (level, nb_col){
                    var head_cells = $(header_rows[level]).children();
                    if (!level_field_position[level]){
                        level_field_position[level] = 0;
                    }
                    if (nb_col < 1){
                        nb_col = head_cells.length;
                    }else{
                        nb_col = nb_col + level_field_position[level];
                    }
                    for (var i = level_field_position[level]; i < nb_col; i++) {
                        cell = $(head_cells[i]);
                        level_field_position[level]++;
                        if(!self.is_multiheader || cell.hasClass('oe_multiheader-field')){
                            rules.push(
                                {selector:
                                      self.selector +
                                        'tbody th:nth-child(' + index + '),' +
                                      self.selector +
                                        'tbody td:nth-child(' + index + '),' +
                                      self.selector +
                                        'tfoot td:nth-child(' + index + '),' +
                                      self.selector +
                                        (self.is_multiheader ? 'thead tr:nth-child(' +
                                                               (level + offset_row) + ') ' : '') +
                                        'th:nth-child(' +  level_field_position[level] + ')',
                                 widthObj: self.get_column_width(cell)});
                            index++;
                        }else{
                            col_with_calculation((level + 1),
                                parseInt(cell.getAttributes().colspan));
                        }
                    }
                };
                col_with_calculation(offset_row, -1);
                var MARGE_WIDTH = 14;
                var page_width = $(document).width() - $(document).find('.oe_leftbar').width();
                var columns_width = 0;
                var auto_size_columns = $.grep(rules,
                    function(rule, i){
                        columns_width += rule.widthObj.width + MARGE_WIDTH;
                        return rule.widthObj.widthDefinedByUser ||
                               rule.widthObj.name === "oe_list_header_selector";
                    }, true);
                var userDefineOnly = false;
                var dx = 0;
                if(page_width > columns_width){
                    var length = 1;
                    if(auto_size_columns.length === 0){
                        length = rules.length;
                        userDefineOnly = true;
                    }else{
                        length = auto_size_columns.length;
                    }
                    if (length !== 0){
                        dx = (page_width - columns_width) / length;
                    }
                }
                $.each(rules, function(){
                    var DX = (!this.widthObj.widthDefinedByUser ||
                             userDefineOnly) &&
                             this.widthObj.name != "oe_list_header_selector" ? dx : 0;
                    self.addCSSRule(self.style, this.selector,
                        'max-width:' + (this.widthObj.width + DX) + 'px;' +
                        'width:' + (this.widthObj.width + DX) + 'px;' +
                        'min-width:' + (this.widthObj.width + DX) + 'px;');
                });
            }
        },
        get_column_id: function(cell){
            var column_name = "";
            if($(cell).find(".oe_list_record_selector").length !== 0){
                column_name = "oe_list_header_selector";
            } else {
                if(cell && cell.getAttributes() && cell.getAttributes()['data-id']){
                    column_name = cell.getAttributes()['data-id'];
                }else{
                    if(this.grouped){
                        var grouped_cell = this.$el.find(
                            'thead > tr:last > th:first-child');
                        if(cell && grouped_cell &&
                           cell.html() === grouped_cell.html()){
                            column_name = "oe_list_header_group";
                        }
                    }
                }
            }
            return column_name;
        },
        get_column_width: function (cell){
            var width = -1;
            var defined = false;
            var column_name = this.get_column_id(cell);
            if(this.columns_width){
                if(this.columns_width[column_name]){
                    width = this.columns_width[column_name];
                    defined = true;
                }
            }
            if(width === -1){
                // default values DEFAULT_COLUMN_WIDTH
                classes = cell.getAttributes()['class'];
                if(classes && classes.length > 0){
                    var self = this;
                    $.each(classes.split(" "), function(col_class){
                        if(self.DEFAULT_COLUMN_WIDTH[this]){
                            width = self.DEFAULT_COLUMN_WIDTH[this];
                        }
                    });
                }
                if(width === -1 && this.DEFAULT_COLUMN_WIDTH[column_name]){
                        width = this.DEFAULT_COLUMN_WIDTH[column_name];
                }
                if(width === -1){
                    console.info("There is no default column size. for theses classes: " +
                                 cell.getAttributes()['class']);
                    width = 75;
                }
            }
            return {width: width, widthDefinedByUser: defined, name: column_name};
        },
        manage_listview_height: function(){
            var table = $(this.$el.find('table.oe_list_content'));
            var tfoot = $(table.find('tfoot'));
            table.css('max-height',
                $(window).height() -
                this.$el.position().top -
                tfoot.height()
            );
            tfoot.css('position', 'absolute');
            tfoot.css('bottom', 0);

            /* top attributes is need for FF users.
             * Becomes necessary when sorting columns or diplay groups
             */
            var thead = $(table.find('thead'));
            thead.css('top', this.$el.position().top);
        },
        removeStyle: function(style){
            if(style && style[0] && style[0].sheet){
                $(style).remove();
            }
        },
        initStyle: function(style){
            this.removeStyle(style);
            style = jQuery("<style></style>");
            $(document.head).append(style);
            // WebKit hack :(
            style.append(document.createTextNode(""));
            return style;
        },
        addCSSRule: function (style, selector, rules, index) {
            if(style[0].sheet.insertRule) {
                style[0].sheet.insertRule(selector + "{" + rules + "}", index);
            }
            else {
                style[0].sheet.addRule(selector, rules, index);
            }
        },
    });


    instance.web.Menu.include({
        start: function(){
            var result = this._super.apply(this, arguments);
            this.compute_leftbar_height();
            instance.web.bus.on('resize', this, this.compute_leftbar_height);
            return result;
        },

        compute_leftbar_height: function(){
            //left menu height
            instance.scrollable_listview.preventFOUC(
                this, 100, this.compute_leftbar_height);
            var leftbar = this.$secondary_menus;
            var bottom_elements_height = 0;
            var afterLeftBar = false;
            $.each(this.$secondary_menus.parent().children(),
               function(element){
                    if(afterLeftBar){
                        bottom_elements_height += element.height();
                    }
                    if(element === leftbar){
                        afterLeftBar = true;
                    }
               });
            leftbar.css('max-height',
                $(window).height() - leftbar.position().top -
                bottom_elements_height - 20
            );
        },

        destroy: function(){
            instance.web.bus.off('resize', this, this.compute_leftbar_height);
            return this._super();
        }
    });

};


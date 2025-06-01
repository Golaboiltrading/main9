<?php
// Oil & Gas Finder - Custom WordPress Functions
// Add this to your theme's functions.php file

// Enqueue custom styles and scripts
function oilgas_enqueue_scripts() {
    // Custom CSS for oil & gas industry styling
    wp_enqueue_style('oilgas-custom-style', get_template_directory_uri() . '/css/oilgas-custom.css', array(), '1.0.0');
    
    // Custom JavaScript for dynamic features
    wp_enqueue_script('oilgas-custom-js', get_template_directory_uri() . '/js/oilgas-custom.js', array('jquery'), '1.0.0', true);
    
    // Font Awesome for icons
    wp_enqueue_style('font-awesome', 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css');
    
    // Google Fonts
    wp_enqueue_style('google-fonts', 'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
}
add_action('wp_enqueue_scripts', 'oilgas_enqueue_scripts');

// Add theme support for various features
function oilgas_theme_setup() {
    // Add theme support for custom logo
    add_theme_support('custom-logo', array(
        'height'      => 80,
        'width'       => 300,
        'flex-height' => true,
        'flex-width'  => true,
    ));
    
    // Add theme support for post thumbnails
    add_theme_support('post-thumbnails');
    
    // Add theme support for custom header
    add_theme_support('custom-header', array(
        'default-image' => get_template_directory_uri() . '/images/oil-rig-header.jpg',
        'width'         => 1920,
        'height'        => 1080,
        'flex-height'   => true,
        'flex-width'    => true,
    ));
    
    // Add theme support for menus
    register_nav_menus(array(
        'primary' => 'Primary Navigation',
        'footer'  => 'Footer Navigation',
    ));
}
add_action('after_setup_theme', 'oilgas_theme_setup');

// Register widget areas
function oilgas_widgets_init() {
    // Sidebar widget area
    register_sidebar(array(
        'name'          => 'News Sidebar',
        'id'            => 'news-sidebar',
        'description'   => 'Widget area for oil & gas news and market data',
        'before_widget' => '<div class="widget %2$s">',
        'after_widget'  => '</div>',
        'before_title'  => '<h3 class="widget-title">',
        'after_title'   => '</h3>',
    ));
    
    // Footer widget areas
    register_sidebar(array(
        'name'          => 'Footer Column 1',
        'id'            => 'footer-1',
        'description'   => 'First footer column',
        'before_widget' => '<div class="footer-widget %2$s">',
        'after_widget'  => '</div>',
        'before_title'  => '<h4 class="footer-widget-title">',
        'after_title'   => '</h4>',
    ));
    
    register_sidebar(array(
        'name'          => 'Footer Column 2',
        'id'            => 'footer-2',
        'description'   => 'Second footer column',
        'before_widget' => '<div class="footer-widget %2$s">',
        'after_widget'  => '</div>',
        'before_title'  => '<h4 class="footer-widget-title">',
        'after_title'   => '</h4>',
    ));
    
    register_sidebar(array(
        'name'          => 'Footer Column 3',
        'id'            => 'footer-3',
        'description'   => 'Third footer column',
        'before_widget' => '<div class="footer-widget %2$s">',
        'after_widget'  => '</div>',
        'before_title'  => '<h4 class="footer-widget-title">',
        'after_title'   => '</h4>',
    ));
}
add_action('widgets_init', 'oilgas_widgets_init');

// Custom post type for Market Data
function create_market_data_post_type() {
    register_post_type('market_data',
        array(
            'labels' => array(
                'name' => 'Market Data',
                'singular_name' => 'Market Data Entry',
                'add_new' => 'Add New Entry',
                'add_new_item' => 'Add New Market Data',
                'edit_item' => 'Edit Market Data',
                'new_item' => 'New Market Data',
                'view_item' => 'View Market Data',
                'search_items' => 'Search Market Data',
                'not_found' => 'No market data found',
                'not_found_in_trash' => 'No market data found in trash'
            ),
            'public' => true,
            'has_archive' => true,
            'menu_icon' => 'dashicons-chart-line',
            'supports' => array('title', 'editor', 'custom-fields'),
            'capability_type' => 'post',
            'rewrite' => array('slug' => 'market-data'),
        )
    );
}
add_action('init', 'create_market_data_post_type');

// Custom post type for Trading Opportunities  
function create_trading_opportunities_post_type() {
    register_post_type('trading_opportunity',
        array(
            'labels' => array(
                'name' => 'Trading Opportunities',
                'singular_name' => 'Trading Opportunity',
                'add_new' => 'Add New Opportunity',
                'add_new_item' => 'Add New Trading Opportunity',
                'edit_item' => 'Edit Trading Opportunity',
                'new_item' => 'New Trading Opportunity',
                'view_item' => 'View Trading Opportunity',
                'search_items' => 'Search Trading Opportunities',
                'not_found' => 'No opportunities found',
                'not_found_in_trash' => 'No opportunities found in trash'
            ),
            'public' => true,
            'has_archive' => true,
            'menu_icon' => 'dashicons-businessman',
            'supports' => array('title', 'editor', 'custom-fields', 'thumbnail'),
            'capability_type' => 'post',
            'rewrite' => array('slug' => 'opportunities'),
        )
    );
}
add_action('init', 'create_trading_opportunities_post_type');

// Custom meta boxes for market data
function add_market_data_meta_boxes() {
    add_meta_box(
        'market_data_details',
        'Market Data Details',
        'market_data_meta_box_callback',
        'market_data',
        'normal',
        'high'
    );
}
add_action('add_meta_boxes', 'add_market_data_meta_boxes');

function market_data_meta_box_callback($post) {
    wp_nonce_field('market_data_meta_box', 'market_data_meta_box_nonce');
    
    $commodity = get_post_meta($post->ID, '_commodity', true);
    $price = get_post_meta($post->ID, '_price', true);
    $change = get_post_meta($post->ID, '_price_change', true);
    $volume = get_post_meta($post->ID, '_volume', true);
    $location = get_post_meta($post->ID, '_location', true);
    
    echo '<table class="form-table">';
    echo '<tr><th><label for="commodity">Commodity:</label></th>';
    echo '<td><select name="commodity" id="commodity">';
    echo '<option value="crude_oil"' . selected($commodity, 'crude_oil', false) . '>Crude Oil</option>';
    echo '<option value="natural_gas"' . selected($commodity, 'natural_gas', false) . '>Natural Gas</option>';
    echo '<option value="lng"' . selected($commodity, 'lng', false) . '>LNG</option>';
    echo '<option value="gasoline"' . selected($commodity, 'gasoline', false) . '>Gasoline</option>';
    echo '<option value="diesel"' . selected($commodity, 'diesel', false) . '>Diesel</option>';
    echo '</select></td></tr>';
    
    echo '<tr><th><label for="price">Price ($):</label></th>';
    echo '<td><input type="text" name="price" id="price" value="' . esc_attr($price) . '" /></td></tr>';
    
    echo '<tr><th><label for="change">Price Change (%):</label></th>';
    echo '<td><input type="text" name="change" id="change" value="' . esc_attr($change) . '" /></td></tr>';
    
    echo '<tr><th><label for="volume">Volume:</label></th>';
    echo '<td><input type="text" name="volume" id="volume" value="' . esc_attr($volume) . '" /></td></tr>';
    
    echo '<tr><th><label for="location">Location:</label></th>';
    echo '<td><input type="text" name="location" id="location" value="' . esc_attr($location) . '" /></td></tr>';
    echo '</table>';
}

// Save market data meta box data
function save_market_data_meta_box($post_id) {
    if (!isset($_POST['market_data_meta_box_nonce'])) return;
    if (!wp_verify_nonce($_POST['market_data_meta_box_nonce'], 'market_data_meta_box')) return;
    if (defined('DOING_AUTOSAVE') && DOING_AUTOSAVE) return;
    if (!current_user_can('edit_post', $post_id)) return;
    
    if (isset($_POST['commodity'])) {
        update_post_meta($post_id, '_commodity', sanitize_text_field($_POST['commodity']));
    }
    if (isset($_POST['price'])) {
        update_post_meta($post_id, '_price', sanitize_text_field($_POST['price']));
    }
    if (isset($_POST['change'])) {
        update_post_meta($post_id, '_price_change', sanitize_text_field($_POST['change']));
    }
    if (isset($_POST['volume'])) {
        update_post_meta($post_id, '_volume', sanitize_text_field($_POST['volume']));
    }
    if (isset($_POST['location'])) {
        update_post_meta($post_id, '_location', sanitize_text_field($_POST['location']));
    }
}
add_action('save_post', 'save_market_data_meta_box');

// Shortcode for market data widget
function market_data_widget_shortcode($atts) {
    $atts = shortcode_atts(array(
        'commodity' => 'all',
        'limit' => 5
    ), $atts);
    
    $args = array(
        'post_type' => 'market_data',
        'posts_per_page' => $atts['limit'],
        'meta_query' => array()
    );
    
    if ($atts['commodity'] !== 'all') {
        $args['meta_query'][] = array(
            'key' => '_commodity',
            'value' => $atts['commodity'],
            'compare' => '='
        );
    }
    
    $market_data = new WP_Query($args);
    
    $output = '<div class="market-data-widget">';
    $output .= '<h3>Live Market Data</h3>';
    $output .= '<div class="market-data-table">';
    
    if ($market_data->have_posts()) {
        while ($market_data->have_posts()) {
            $market_data->the_post();
            $commodity = get_post_meta(get_the_ID(), '_commodity', true);
            $price = get_post_meta(get_the_ID(), '_price', true);
            $change = get_post_meta(get_the_ID(), '_price_change', true);
            $volume = get_post_meta(get_the_ID(), '_volume', true);
            
            $change_class = floatval($change) >= 0 ? 'positive' : 'negative';
            $change_icon = floatval($change) >= 0 ? '▲' : '▼';
            
            $output .= '<div class="market-data-row">';
            $output .= '<div class="commodity">' . ucwords(str_replace('_', ' ', $commodity)) . '</div>';
            $output .= '<div class="price">$' . $price . '</div>';
            $output .= '<div class="change ' . $change_class . '">' . $change_icon . ' ' . $change . '%</div>';
            $output .= '</div>';
        }
    } else {
        $output .= '<p>No market data available.</p>';
    }
    
    $output .= '</div>';
    $output .= '<div class="market-data-footer">';
    $output .= '<a href="' . site_url('/market-data') . '" class="view-all-link">View All Market Data →</a>';
    $output .= '</div>';
    $output .= '</div>';
    
    wp_reset_postdata();
    
    return $output;
}
add_shortcode('market_data', 'market_data_widget_shortcode');

// Shortcode for trading platform CTA
function trading_platform_cta_shortcode($atts) {
    $atts = shortcode_atts(array(
        'text' => 'Access Trading Platform',
        'url' => 'https://app.oilgasfinder.com',
        'style' => 'primary'
    ), $atts);
    
    $output = '<div class="trading-platform-cta">';
    $output .= '<a href="' . esc_url($atts['url']) . '" class="cta-button ' . esc_attr($atts['style']) . '" target="_blank">';
    $output .= esc_html($atts['text']);
    $output .= '</a>';
    $output .= '</div>';
    
    return $output;
}
add_shortcode('trading_cta', 'trading_platform_cta_shortcode');

// Custom dashboard widget for oil & gas metrics
function add_oilgas_dashboard_widget() {
    wp_add_dashboard_widget(
        'oilgas_metrics_widget',
        'Oil & Gas Finder Metrics',
        'oilgas_dashboard_widget_content'
    );
}
add_action('wp_dashboard_setup', 'add_oilgas_dashboard_widget');

function oilgas_dashboard_widget_content() {
    $total_posts = wp_count_posts('post')->publish;
    $total_market_data = wp_count_posts('market_data')->publish;
    $total_opportunities = wp_count_posts('trading_opportunity')->publish;
    
    echo '<div class="oilgas-dashboard-metrics">';
    echo '<div class="metric"><strong>' . $total_posts . '</strong> Blog Posts</div>';
    echo '<div class="metric"><strong>' . $total_market_data . '</strong> Market Data Entries</div>';
    echo '<div class="metric"><strong>' . $total_opportunities . '</strong> Trading Opportunities</div>';
    echo '</div>';
    
    echo '<div class="oilgas-quick-actions">';
    echo '<a href="' . admin_url('post-new.php') . '" class="button">Add Blog Post</a>';
    echo '<a href="' . admin_url('post-new.php?post_type=market_data') . '" class="button">Add Market Data</a>';
    echo '<a href="' . admin_url('post-new.php?post_type=trading_opportunity') . '" class="button">Add Opportunity</a>';
    echo '</div>';
}

// Add custom CSS to admin
function oilgas_admin_styles() {
    echo '<style>
        .oilgas-dashboard-metrics {
            display: flex;
            gap: 20px;
            margin-bottom: 15px;
        }
        .oilgas-dashboard-metrics .metric {
            background: #f1f1f1;
            padding: 10px;
            border-radius: 4px;
            text-align: center;
            flex: 1;
        }
        .oilgas-quick-actions {
            display: flex;
            gap: 10px;
        }
        .oilgas-quick-actions .button {
            flex: 1;
            text-align: center;
        }
    </style>';
}
add_action('admin_head', 'oilgas_admin_styles');

// Custom excerpt length for oil & gas content
function oilgas_excerpt_length($length) {
    return 25;
}
add_filter('excerpt_length', 'oilgas_excerpt_length');

// Custom excerpt more text
function oilgas_excerpt_more($more) {
    return ' <a href="' . get_permalink() . '" class="read-more-link">Read More →</a>';
}
add_filter('excerpt_more', 'oilgas_excerpt_more');

// Add schema markup for organization
function add_oilgas_schema_markup() {
    if (is_front_page()) {
        $schema = array(
            '@context' => 'https://schema.org',
            '@type' => 'Organization',
            'name' => 'Oil & Gas Finder',
            'description' => 'Global oil and gas trading platform connecting verified traders worldwide',
            'url' => home_url(),
            'logo' => array(
                '@type' => 'ImageObject',
                'url' => get_theme_mod('custom_logo') ? wp_get_attachment_url(get_theme_mod('custom_logo')) : get_template_directory_uri() . '/images/logo.png'
            ),
            'contactPoint' => array(
                '@type' => 'ContactPoint',
                'telephone' => '+1-713-XXX-XXXX',
                'contactType' => 'customer service',
                'availableLanguage' => array('English', 'Arabic')
            ),
            'address' => array(
                '@type' => 'PostalAddress',
                'streetAddress' => '1000 Louisiana Street',
                'addressLocality' => 'Houston',
                'addressRegion' => 'TX',
                'postalCode' => '77002',
                'addressCountry' => 'US'
            ),
            'sameAs' => array(
                'https://www.linkedin.com/company/oil-gas-finder',
                'https://twitter.com/oilgasfinder'
            ),
            'industry' => 'Oil and Gas Trading'
        );
        
        echo '<script type="application/ld+json">' . json_encode($schema) . '</script>';
    }
}
add_action('wp_head', 'add_oilgas_schema_markup');

// Security enhancements
function oilgas_security_headers() {
    header('X-Content-Type-Options: nosniff');
    header('X-Frame-Options: SAMEORIGIN');
    header('X-XSS-Protection: 1; mode=block');
    header('Referrer-Policy: strict-origin-when-cross-origin');
}
add_action('send_headers', 'oilgas_security_headers');

// Performance optimizations
function oilgas_performance_optimizations() {
    // Remove unused WordPress features
    remove_action('wp_head', 'wp_generator');
    remove_action('wp_head', 'wlwmanifest_link');
    remove_action('wp_head', 'rsd_link');
    remove_action('wp_head', 'wp_shortlink_wp_head');
    
    // Disable emoji scripts
    remove_action('wp_head', 'print_emoji_detection_script', 7);
    remove_action('wp_print_styles', 'print_emoji_styles');
}
add_action('init', 'oilgas_performance_optimizations');
?>
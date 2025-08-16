// Shopify Store Insights Analyzer - Frontend JavaScript
// This handles all the UI interactions and API calls

class ShopifyAnalyzer {
    constructor() {
        this.apiBaseUrl = '/api';
        this.currentData = null;
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // Handle form submission
        document.getElementById('analyzeForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.analyzeStore();
        });

        // URL validation button
        document.getElementById('validateBtn').addEventListener('click', () => {
            this.validateUrl();
        });

        // Support for Enter key in input field
        document.getElementById('websiteUrl').addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.analyzeStore();
            }
        });
    }

    async analyzeStore() {
        const urlInput = document.getElementById('websiteUrl');
        const websiteUrl = urlInput.value.trim();

        if (!websiteUrl) {
            this.showError('Please enter a website URL');
            return;
        }

        try {
            this.showLoading(true);
            this.hideResults();

            const response = await fetch(`${this.apiBaseUrl}/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ website_url: websiteUrl })
            });

            const data = await response.json();
            this.showLoading(false);

            if (response.ok) {
                this.currentData = data;
                this.showSuccess();
                this.displayResults(data);
            } else {
                this.showError(data.error || 'Analysis failed', data.details);
            }

        } catch (error) {
            this.showLoading(false);
            this.showError('Network error occurred. Please try again.');
            console.error('Analysis error:', error);
        }
    }

    async validateUrl() {
        const urlInput = document.getElementById('websiteUrl');
        const websiteUrl = urlInput.value.trim();

        if (!websiteUrl) {
            this.showError('Please enter a website URL');
            return;
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}/validate-url`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ website_url: websiteUrl })
            });

            const data = await response.json();

            if (response.ok) {
                if (data.is_valid_shopify_store) {
                    this.showSuccess('Valid Shopify store detected! You can proceed with analysis.');
                } else {
                    this.showError('This doesn\'t appear to be a valid Shopify store.');
                }
            } else {
                this.showError(data.error || 'Validation failed');
            }

        } catch (error) {
            this.showError('Network error occurred during validation.');
            console.error('Validation error:', error);
        }
    }

    showLoading(show) {
        const loadingIndicator = document.getElementById('loadingIndicator');
        const analyzeBtn = document.getElementById('analyzeBtn');
        
        if (show) {
            loadingIndicator.classList.remove('d-none');
            analyzeBtn.disabled = true;
            analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Analyzing...';
        } else {
            loadingIndicator.classList.add('d-none');
            analyzeBtn.disabled = false;
            analyzeBtn.innerHTML = '<i class="fas fa-analytics me-2"></i>Analyze Store';
        }
    }

    showSuccess(message = null) {
        const successAlert = document.getElementById('successAlert');
        const errorAlert = document.getElementById('errorAlert');
        
        errorAlert.classList.add('d-none');
        
        if (message) {
            successAlert.querySelector('p').textContent = message;
        }
        
        successAlert.classList.remove('d-none');
        this.showResults();
    }

    showError(message, details = null) {
        const errorAlert = document.getElementById('errorAlert');
        const successAlert = document.getElementById('successAlert');
        const errorMessage = document.getElementById('errorMessage');
        
        successAlert.classList.add('d-none');
        
        let fullMessage = message;
        if (details) {
            fullMessage += ` Details: ${details}`;
        }
        
        errorMessage.textContent = fullMessage;
        errorAlert.classList.remove('d-none');
        this.showResults();
    }

    showResults() {
        document.getElementById('resultsSection').classList.remove('d-none');
        document.getElementById('resultsSection').scrollIntoView({ behavior: 'smooth' });
    }

    hideResults() {
        document.getElementById('resultsSection').classList.add('d-none');
        document.getElementById('analysisResults').classList.add('d-none');
    }

    displayResults(data) {
        document.getElementById('analysisResults').classList.remove('d-none');
        
        this.displayBrandOverview(data.data);
        this.displayMetrics(data.analysis);
        this.displayProducts(data.data);
        this.displayContact(data.data);
        this.displaySocial(data.data);
        this.displayPolicies(data.data);
        this.displayFAQs(data.data);
        this.displayImportantLinks(data.data);
    }

    displayBrandOverview(data) {
        const container = document.getElementById('brandOverview');
        
        container.innerHTML = `
            <div class="row">
                <div class="col-md-8">
                    <h4 class="text-primary">${data.brand_name || 'Brand Name Not Available'}</h4>
                    <p class="text-muted mb-3">${data.brand_description || 'No brand description available'}</p>
                    <div class="mb-3">
                        <strong>Website:</strong> 
                        <a href="${data.website_url}" target="_blank" class="text-decoration-none">
                            ${data.website_url}
                            <i class="fas fa-external-link-alt ms-1"></i>
                        </a>
                    </div>
                    <div class="text-muted">
                        <small>
                            <i class="fas fa-clock me-1"></i>
                            Analyzed: ${data.scraped_at ? new Date(data.scraped_at).toLocaleString('en-IN', {timeZone: 'Asia/Kolkata'}) : 'Just now'} IST
                        </small>
                    </div>
                </div>
                <div class="col-md-4 text-center">
                    <div class="metric-card p-3">
                        <h5 class="mb-0">${data.product_catalog.length}</h5>
                        <small>Total Products</small>
                    </div>
                </div>
            </div>
        `;
    }

    displayMetrics(analysis) {
        const container = document.getElementById('metricsContent');
        const metrics = analysis.basic_metrics;
        const completeness = (analysis.completeness_score * 100).toFixed(1);
        
        container.innerHTML = `
            <div class="row g-3 mb-4">
                <div class="col-md-3">
                    <div class="card bg-primary text-white text-center">
                        <div class="card-body">
                            <h4 class="mb-0">${metrics.total_products}</h4>
                            <small>Products</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-info text-white text-center">
                        <div class="card-body">
                            <h4 class="mb-0">${metrics.hero_products_count}</h4>
                            <small>Hero Products</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-success text-white text-center">
                        <div class="card-body">
                            <h4 class="mb-0">${metrics.faq_count}</h4>
                            <small>FAQs</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-warning text-white text-center">
                        <div class="card-body">
                            <h4 class="mb-0">${completeness}%</h4>
                            <small>Completeness</small>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row">
                <div class="col-md-6">
                    <h6>Data Availability:</h6>
                    <ul class="list-unstyled">
                        <li>${this.getStatusBadge(metrics.has_privacy_policy)} Privacy Policy</li>
                        <li>${this.getStatusBadge(metrics.has_return_policy)} Return Policy</li>
                        <li>${this.getStatusBadge(metrics.contact_methods > 0)} Contact Information</li>
                        <li>${this.getStatusBadge(metrics.social_platforms > 0)} Social Media</li>
                    </ul>
                </div>
                <div class="col-md-6">
                    <h6>Content Quality:</h6>
                    <div class="mb-2">
                        <small class="text-muted">Brand Description:</small>
                        <span class="badge ${this.getQualityBadgeClass(analysis.content_quality.brand_description)}">
                            ${analysis.content_quality.brand_description}
                        </span>
                    </div>
                    <div class="mb-2">
                        <small class="text-muted">FAQs:</small>
                        <span class="badge ${this.getQualityBadgeClass(analysis.content_quality.faqs)}">
                            ${analysis.content_quality.faqs}
                        </span>
                    </div>
                </div>
            </div>
        `;
    }

    displayProducts(data) {
        const container = document.getElementById('productsContent');
        
        if (!data.product_catalog || data.product_catalog.length === 0) {
            container.innerHTML = '<p class="text-muted">No products found in the catalog.</p>';
            return;
        }

        const productsToShow = data.product_catalog.slice(0, 6); // Show first 6 products
        
        container.innerHTML = `
            <div class="row g-3">
                ${productsToShow.map(product => `
                    <div class="col-md-4 col-lg-3">
                        <div class="product-card p-3 h-100">
                            ${product.images && product.images[0] ? 
                                `<img src="${product.images[0]}" alt="${product.title}" class="product-image mb-2">` :
                                '<div class="product-image mb-2 bg-secondary d-flex align-items-center justify-content-center"><i class="fas fa-image fa-2x text-muted"></i></div>'
                            }
                            <h6 class="mb-2">${product.title || 'Untitled Product'}</h6>
                            ${product.price ? `<p class="text-success mb-2"><strong>${product.price}</strong></p>` : ''}
                            ${product.vendor ? `<small class="text-muted">by ${product.vendor}</small>` : ''}
                            ${product.url ? `<div class="mt-2"><a href="${product.url}" target="_blank" class="btn btn-sm btn-outline-primary">View Product</a></div>` : ''}
                        </div>
                    </div>
                `).join('')}
            </div>
            
            ${data.product_catalog.length > 6 ? 
                `<div class="text-center mt-3">
                    <small class="text-muted">Showing 6 of ${data.product_catalog.length} products</small>
                </div>` : ''
            }
        `;
    }

    displayContact(data) {
        const container = document.getElementById('contactContent');
        
        if (!data.contact_info) {
            container.innerHTML = '<p class="text-muted">No contact information found.</p>';
            return;
        }

        container.innerHTML = `
            ${data.contact_info.emails && data.contact_info.emails.length > 0 ? `
                <div class="mb-3">
                    <h6><i class="fas fa-envelope me-2"></i>Email Addresses:</h6>
                    ${data.contact_info.emails.map(email => 
                        `<div class="contact-item">
                            <a href="mailto:${email}" class="text-decoration-none">${email}</a>
                        </div>`
                    ).join('')}
                </div>
            ` : ''}
            
            ${data.contact_info.phone_numbers && data.contact_info.phone_numbers.length > 0 ? `
                <div class="mb-3">
                    <h6><i class="fas fa-phone me-2"></i>Phone Numbers:</h6>
                    ${data.contact_info.phone_numbers.map(phone => 
                        `<div class="contact-item">
                            <a href="tel:${phone}" class="text-decoration-none">${phone}</a>
                        </div>`
                    ).join('')}
                </div>
            ` : ''}
            
            ${data.contact_info.address ? `
                <div>
                    <h6><i class="fas fa-map-marker-alt me-2"></i>Address:</h6>
                    <p class="mb-0">${data.contact_info.address}</p>
                </div>
            ` : ''}
            
            ${(!data.contact_info.emails || data.contact_info.emails.length === 0) && 
              (!data.contact_info.phone_numbers || data.contact_info.phone_numbers.length === 0) && 
              !data.contact_info.address ? 
                '<p class="text-muted">No contact information available.</p>' : ''
            }
        `;
    }

    displaySocial(data) {
        const container = document.getElementById('socialContent');
        
        if (!data.social_handles || data.social_handles.length === 0) {
            container.innerHTML = '<p class="text-muted">No social media handles found.</p>';
            return;
        }

        container.innerHTML = `
            <div class="d-flex flex-wrap gap-2">
                ${data.social_handles.map(social => `
                    <a href="${social.url}" target="_blank" class="btn btn-outline-primary btn-sm text-decoration-none">
                        <i class="fab fa-${social.platform} me-2"></i>
                        ${social.platform.charAt(0).toUpperCase() + social.platform.slice(1)}
                        ${social.handle ? `(${social.handle})` : ''}
                    </a>
                `).join('')}
            </div>
        `;
    }

    displayPolicies(data) {
        const container = document.getElementById('policiesContent');
        
        container.innerHTML = `
            <div class="mb-3">
                <h6><i class="fas fa-shield-alt me-2"></i>Privacy Policy:</h6>
                ${data.privacy_policy && data.privacy_policy.url ? 
                    `<a href="${data.privacy_policy.url}" target="_blank" class="btn btn-sm btn-outline-primary mb-2">
                        View Privacy Policy <i class="fas fa-external-link-alt ms-1"></i>
                    </a>
                    ${data.privacy_policy.content_preview ? 
                        `<div class="small text-muted mt-2">${data.privacy_policy.content_preview}</div>` : ''
                    }` : 
                    '<span class="text-muted">Not found</span>'
                }
            </div>
            
            <div>
                <h6><i class="fas fa-undo me-2"></i>Return/Refund Policy:</h6>
                ${data.return_refund_policy && data.return_refund_policy.url ? 
                    `<a href="${data.return_refund_policy.url}" target="_blank" class="btn btn-sm btn-outline-primary mb-2">
                        View Return Policy <i class="fas fa-external-link-alt ms-1"></i>
                    </a>
                    ${data.return_refund_policy.content_preview ? 
                        `<div class="small text-muted mt-2">${data.return_refund_policy.content_preview}</div>` : ''
                    }` : 
                    '<span class="text-muted">Not found</span>'
                }
            </div>
        `;
    }

    displayFAQs(data) {
        const container = document.getElementById('faqsContent');
        
        if (!data.faqs || data.faqs.length === 0) {
            container.innerHTML = '<p class="text-muted">No FAQs found.</p>';
            return;
        }

        container.innerHTML = `
            <div class="accordion" id="faqAccordion">
                ${data.faqs.slice(0, 5).map((faq, index) => `
                    <div class="accordion-item">
                        <h2 class="accordion-header" id="faq-heading-${index}">
                            <button class="accordion-button ${index === 0 ? '' : 'collapsed'}" type="button" 
                                data-bs-toggle="collapse" data-bs-target="#faq-collapse-${index}">
                                ${faq.question}
                            </button>
                        </h2>
                        <div id="faq-collapse-${index}" class="accordion-collapse collapse ${index === 0 ? 'show' : ''}" 
                            data-bs-parent="#faqAccordion">
                            <div class="accordion-body">
                                ${faq.answer}
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
            
            ${data.faqs.length > 5 ? 
                `<div class="text-center mt-3">
                    <small class="text-muted">Showing 5 of ${data.faqs.length} FAQs</small>
                </div>` : ''
            }
        `;
    }

    displayImportantLinks(data) {
        const container = document.getElementById('linksContent');
        
        if (!data.important_links || Object.keys(data.important_links).length === 0) {
            container.innerHTML = '<p class="text-muted">No important links found.</p>';
            return;
        }

        container.innerHTML = `
            <div class="row g-2">
                ${Object.entries(data.important_links).map(([category, url]) => `
                    <div class="col-md-6">
                        <a href="${url}" target="_blank" class="btn btn-outline-secondary btn-sm w-100 text-start">
                            <i class="fas fa-link me-2"></i>
                            ${category.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                            <i class="fas fa-external-link-alt ms-auto"></i>
                        </a>
                    </div>
                `).join('')}
            </div>
        `;
    }


    getStatusBadge(status) {
        return status ? 
            '<span class="badge bg-success me-2"><i class="fas fa-check"></i></span>' : 
            '<span class="badge bg-danger me-2"><i class="fas fa-times"></i></span>';
    }

    getQualityBadgeClass(quality) {
        switch(quality) {
            case 'good': return 'bg-success';
            case 'basic': return 'bg-warning';
            case 'missing': return 'bg-danger';
            default: return 'bg-secondary';
        }
    }
}

// Initialize the analyzer when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new ShopifyAnalyzer();
});

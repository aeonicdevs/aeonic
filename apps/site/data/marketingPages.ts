export type Metric = {
  value: string
  label: string
}

export type Feature = {
  label: string
  title: string
  text: string
}

export type MarketingPageData = {
  eyebrow: string
  title: string
  lead: string
  heroImage?: string
  primaryAction?: [string, string]
  secondaryAction?: [string, string]
  metrics?: Metric[]
  sections?: {
    eyebrow: string
    title: string
    lead?: string
    features: Feature[]
  }[]
  note?: string
}

export const marketingPages: Record<string, MarketingPageData> = {
  programs: {
    eyebrow: 'Aeonic Continuum',
    title: 'The complete care program behind modern longevity.',
    lead:
      'Physician-led, lab-guided protocols for weight, hormones, performance, recovery, and long-term health, deployed in-clinic or direct to patients.',
    heroImage: '/assets/hero-health.webp',
    primaryAction: ['Explore treatments', '/treatments'],
    secondaryAction: ['Book a demo', '/connect-inquiry'],
    metrics: [
      { value: 'Lab-guided', label: 'Plans adapt as markers move' },
      { value: 'Care lines', label: 'Protocols for modern longevity demand' },
      { value: 'Provider led', label: 'Licensed review and oversight' }
    ],
    sections: [
      {
        eyebrow: 'How care works',
        title: 'Start from a proven protocol, then tune around the patient.',
        features: [
          {
            label: 'Intake',
            title: 'Screened before treatment',
            text: 'Structured intake, history, goals, contraindications, and consent route patients before review.'
          },
          {
            label: 'Biomarkers',
            title: 'Labs drive the plan',
            text: 'Bloodwork anchors dosing, supplement support, monitoring cadence, and protocol changes.'
          },
          {
            label: 'Iteration',
            title: 'Measured over time',
            text: 'The program is built for retesting, refills, education, messaging, and ongoing adjustment.'
          }
        ]
      }
    ]
  },
  nexus: {
    eyebrow: 'Aeonic Nexus',
    title: 'The clinical platform behind modern longevity practices.',
    lead:
      'A white-labeled operating layer for protocols, provider review, labs, pharmacy, billing, compliance, and patient engagement.',
    heroImage: '/assets/hero-nexus.avif',
    primaryAction: ['Partner login', '/partner-login'],
    secondaryAction: ['Book a demo', '/connect-inquiry'],
    metrics: [
      { value: 'One console', label: 'Patients, tasks, labs, revenue' },
      { value: 'White label', label: 'Your clinic or brand experience' },
      { value: 'Live fast', label: 'Built for rapid deployment' }
    ],
    sections: [
      {
        eyebrow: 'Platform stack',
        title: 'The rails that make the program repeatable.',
        features: [
          {
            label: 'Clinical engine',
            title: 'Protocols and prescribing',
            text: 'Executable protocol logic, review workflows, contraindication checks, and prescription routing.'
          },
          {
            label: 'Operations',
            title: 'Labs, pharmacy, billing',
            text: 'Coordinate orders, results, refills, shipments, recurring plans, and revenue from one place.'
          },
          {
            label: 'Intelligence',
            title: 'Aeva alongside',
            text: 'Aeva helps summarize, explain, draft, and surface context while clinicians remain in control.'
          }
        ]
      }
    ]
  },
  treatments: {
    eyebrow: 'Treatment systems',
    title: 'Care lines with proven protocols, fully customizable.',
    lead:
      'Each Aeonic care line includes therapy options, phased plans, biomarker targets, and clinician-guided supplement support.',
    primaryAction: ['Book a demo', '/connect-inquiry'],
    sections: [
      {
        eyebrow: 'Protocol library',
        title: 'Built around the care patients ask for most.',
        features: [
          {
            label: 'Metabolic',
            title: 'Weight and GLP-1 care',
            text: 'Metabolic protocols that pair prescription oversight with labs, nutrition, and long-term maintenance.'
          },
          {
            label: 'Hormones',
            title: 'Energy, drive, sleep',
            text: 'Hormone optimization guided by bloodwork, symptoms, goals, and licensed clinical review.'
          },
          {
            label: 'Performance',
            title: 'Peptides and recovery',
            text: 'Targeted protocols for recovery, performance, body composition, cognition, and healthy aging.'
          },
          {
            label: 'Longevity',
            title: 'Immune, gut, skin, sleep',
            text: 'Functional care lines designed to be combined thoughtfully as patient biomarkers evolve.'
          }
        ]
      }
    ],
    note:
      'These categories are organizational tools for licensed healthcare providers. All prescribing decisions are made by independently licensed clinicians.'
  },
  catalog: {
    eyebrow: 'Aeonic Store',
    title: 'A clinical formulary and commerce layer under your brand.',
    lead:
      'Prescription categories, AEON nutrition, and connected devices live in the patient app and can be dispensed or drop-shipped without clinic inventory.',
    primaryAction: ['See Nexus', '/nexus'],
    secondaryAction: ['Book a demo', '/connect-inquiry'],
    sections: [
      {
        eyebrow: 'Commerce',
        title: 'Products connected to care, not floating beside it.',
        features: [
          {
            label: 'Formulary',
            title: 'Prescription workflows',
            text: 'Provider-reviewed therapies routed through the configured pharmacy and telehealth workflow.'
          },
          {
            label: 'Nutrition',
            title: 'Clinician-formulated support',
            text: 'Supplement stacks can be paired with protocols, memberships, and patient education.'
          },
          {
            label: 'Devices',
            title: 'Connected monitoring',
            text: 'Wearables and devices can support adherence, measurement, and longitudinal engagement.'
          }
        ]
      }
    ],
    note:
      'Product imagery and categories are informational. Supplements are not intended to diagnose, treat, cure, or prevent disease.'
  },
  partners: {
    eyebrow: 'Partners',
    title: 'The network behind the system.',
    lead:
      'Aeonic coordinates clinical, pharmacy, laboratory, operational, and growth partners into one deployable longevity infrastructure.',
    primaryAction: ['Become a partner', '/connect-inquiry'],
    sections: [
      {
        eyebrow: 'Network',
        title: 'Each partner plugs into a specific part of the care model.',
        features: [
          {
            label: 'Clinical',
            title: 'Licensed oversight',
            text: 'Provider review, prescribing, compliance practices, and clinical governance stay explicit.'
          },
          {
            label: 'Operations',
            title: 'Fulfillment and labs',
            text: 'Labs, pharmacy, dispensing, shipping, and membership operations are coordinated through the platform.'
          },
          {
            label: 'Growth',
            title: 'Launch and scale',
            text: 'Brand, funnel, education, and retention systems help partners bring programs to market.'
          }
        ]
      }
    ]
  },
  'our-story': {
    eyebrow: 'Our Story',
    title: 'Built from clinical practice, then made repeatable.',
    lead:
      'Aeonic translates years of root-cause, functional, and performance medicine into a structured system that clinics can deploy consistently.',
    primaryAction: ['Read the science', '/science'],
    sections: [
      {
        eyebrow: 'Why it exists',
        title: 'Longevity medicine needs infrastructure equal to the demand.',
        features: [
          {
            label: 'Clinical depth',
            title: 'Care before software',
            text: 'The system begins with real patient care, biomarker interpretation, and protocol refinement.'
          },
          {
            label: 'Structure',
            title: 'Standards at scale',
            text: 'Protocols, workflows, and governance help care teams avoid ad hoc delivery as demand grows.'
          },
          {
            label: 'Access',
            title: 'More clinics, better programs',
            text: 'Aeonic gives clinics a way to launch sophisticated care without rebuilding the full stack.'
          }
        ]
      }
    ]
  },
  science: {
    eyebrow: 'Science',
    title: 'Clinical authority built into the operating model.',
    lead:
      'Aeonic is designed for evidence-informed, biomarker-guided care where licensed providers make the clinical decisions.',
    primaryAction: ['Meet Dr. Lacey', '/dr-lacey'],
    sections: [
      {
        eyebrow: 'Clinical frame',
        title: 'A system to care for a system.',
        features: [
          {
            label: 'Root cause',
            title: 'Connected physiology',
            text: 'Hormones, metabolism, sleep, cognition, recovery, and immune function are treated as related systems.'
          },
          {
            label: 'Measurement',
            title: 'Biomarkers over guesses',
            text: 'Labs and symptom context guide plan design, retesting, and adjustment.'
          },
          {
            label: 'Governance',
            title: 'Provider accountability',
            text: 'Aeva and software support decisions, while licensed clinicians review and sign care.'
          }
        ]
      }
    ]
  },
  'dr-lacey': {
    eyebrow: 'Clinical founder',
    title: 'Two decades of clinical practice, built into a system.',
    lead:
      'Dr. Lacey’s clinical work informs the protocol library, biomarker logic, education, and care standards inside Aeonic.',
    heroImage: '/assets/dr-lacey.webp',
    primaryAction: ['Book a demo', '/connect-inquiry'],
    sections: [
      {
        eyebrow: 'Authority',
        title: 'Clinical judgment made operational.',
        features: [
          {
            label: 'Protocols',
            title: 'Refined patient by patient',
            text: 'Care patterns are captured as repeatable workflows without flattening individual clinical judgment.'
          },
          {
            label: 'Education',
            title: 'Built for care teams',
            text: 'Academy content and protocol guidance help clinics implement the model responsibly.'
          },
          {
            label: 'Standards',
            title: 'Consistency with room to customize',
            text: 'The platform supports both pre-built care lines and bespoke protocol design.'
          }
        ]
      }
    ]
  },
  mission: {
    eyebrow: 'Mission',
    title: 'Advance longevity medicine without outrunning safety.',
    lead:
      'Aeonic helps clinics build structured, evidence-informed systems for precision health while maintaining accountability and clinical standards.',
    primaryAction: ['Our story', '/our-story'],
    sections: [
      {
        eyebrow: 'Principles',
        title: 'Infrastructure for responsible growth.',
        features: [
          {
            label: 'Evidence',
            title: 'Informed, not impulsive',
            text: 'Programs are built around biomarkers, clinical review, and practical monitoring.'
          },
          {
            label: 'Access',
            title: 'Deployable care',
            text: 'Clinics can offer advanced programs without inventing every workflow themselves.'
          },
          {
            label: 'Accountability',
            title: 'Clear clinical roles',
            text: 'The system supports providers, patients, and operators without blurring who makes medical decisions.'
          }
        ]
      }
    ]
  },
  press: {
    eyebrow: 'Press',
    title: 'Aeonic Health Systems news and announcements.',
    lead:
      'Updates on the platform, protocols, partnerships, and the infrastructure behind precision longevity medicine.',
    primaryAction: ['Contact', '/contact'],
    sections: [
      {
        eyebrow: 'Media',
        title: 'For inquiries and background.',
        features: [
          {
            label: 'Company',
            title: 'Aeonic Health Systems',
            text: 'Clinical infrastructure for functional, performance, and precision longevity medicine.'
          },
          {
            label: 'Platform',
            title: 'Aeonic Nexus',
            text: 'The operating layer for white-labeled longevity programs and provider workflows.'
          },
          {
            label: 'Program',
            title: 'Aeonic Continuum',
            text: 'The patient-facing protocols, education, and care experience.'
          }
        ]
      }
    ]
  },
  announcements: {
    eyebrow: 'Announcements',
    title: 'Product and partner updates from Aeonic.',
    lead:
      'A place for launch notes, platform updates, clinical program additions, and partnership announcements.',
    primaryAction: ['Book a demo', '/connect-inquiry'],
    sections: [
      {
        eyebrow: 'Latest',
        title: 'The Nuxt rebuild is taking shape.',
        features: [
          {
            label: 'Site',
            title: 'Reference routes rebuilt',
            text: 'Core pages from the static mockup now have structured Nuxt equivalents.'
          },
          {
            label: 'Login',
            title: 'Partner access flow',
            text: 'The front-end sign-in surface is in place and ready for real authentication.'
          },
          {
            label: 'Inquiry',
            title: 'Demo request flow',
            text: 'The partner inquiry form now behaves like a real front-end interaction.'
          }
        ]
      }
    ]
  },
  ways: {
    eyebrow: 'The system',
    title: 'One system: the medicine patients feel and the platform that runs it.',
    lead:
      'Aeonic Continuum is the clinical care experience. Aeonic Nexus is the software, workflow, and operating layer behind it.',
    primaryAction: ['Explore Continuum', '/programs'],
    secondaryAction: ['Explore Nexus', '/nexus'],
    sections: [
      {
        eyebrow: 'Two doors',
        title: 'A patient-facing program and a clinic-facing platform.',
        features: [
          {
            label: 'Continuum',
            title: 'Protocols and care',
            text: 'Treatment systems, education, labs, products, and patient engagement.'
          },
          {
            label: 'Nexus',
            title: 'Practice operations',
            text: 'Provider console, prescribing, pharmacy, billing, compliance, and analytics.'
          },
          {
            label: 'Aeva',
            title: 'Intelligence throughout',
            text: 'Member companion and clinical assistant across the care journey.'
          }
        ]
      }
    ]
  }
}

export const legacyAliases: Record<string, string> = {
  'aeonic-health': 'programs',
  'aeonic-connect': 'nexus',
  'aeonic-systems': 'ways',
  'aeonic-store': 'catalog',
  'connect-inquiry': 'inquiry',
  'aeonic-connect-login': 'partner-login',
  'aeonic-systems-login': 'member-login',
  'aeonic-health-login': 'member-login'
}

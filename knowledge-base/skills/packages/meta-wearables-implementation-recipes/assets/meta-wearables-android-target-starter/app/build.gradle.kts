import java.util.Properties
import org.jetbrains.kotlin.gradle.dsl.JvmTarget

plugins {
  alias(libs.plugins.android.application)
  alias(libs.plugins.jetbrains.kotlin.android)
}

val localProperties =
    Properties().apply {
      val localPropertiesFile = rootProject.file("local.properties")
      if (localPropertiesFile.exists()) {
        localPropertiesFile.inputStream().use(::load)
      }
    }

fun configuredValue(propertyName: String, environmentName: String): String =
    providers.environmentVariable(environmentName).orNull
        ?: providers.gradleProperty(propertyName).orNull
        ?: localProperties.getProperty(propertyName, "")

android {
  namespace = "com.example.metawearables.targetstarter"
  compileSdk = 36

  defaultConfig {
    applicationId = "com.example.metawearables.targetstarter"
    minSdk = 31
    targetSdk = 36
    versionCode = 1
    versionName = "0.1.0"

    manifestPlaceholders["mwdat_application_id"] =
        configuredValue("mwdat_application_id", "MWDAT_APPLICATION_ID")
    manifestPlaceholders["mwdat_client_token"] =
        configuredValue("mwdat_client_token", "MWDAT_CLIENT_TOKEN")
    manifestPlaceholders["mwdat_analytics_opt_out"] =
        configuredValue("mwdat_analytics_opt_out", "MWDAT_ANALYTICS_OPT_OUT").ifBlank { "false" }
    manifestPlaceholders["mwdat_crash_reporting_opt_out"] =
        configuredValue("mwdat_crash_reporting_opt_out", "MWDAT_CRASH_REPORTING_OPT_OUT").ifBlank { "false" }
  }

  buildTypes {
    release {
      isMinifyEnabled = true
      proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
    }
  }

  compileOptions {
    sourceCompatibility = JavaVersion.VERSION_17
    targetCompatibility = JavaVersion.VERSION_17
  }

  packaging { resources { excludes += "/META-INF/{AL2.0,LGPL2.1}" } }
}

kotlin { compilerOptions { jvmTarget = JvmTarget.JVM_17 } }

dependencies {
  implementation(libs.mwdat.core)
  implementation(libs.mwdat.camera)
  implementation(libs.mwdat.display)
  implementation(libs.mwdat.mockdevice)
}

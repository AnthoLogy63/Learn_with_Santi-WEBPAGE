import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useAppContext } from "@/context/AppContext";
import { ArrowLeft, ArrowRight, CheckCircle2, XCircle, RotateCcw, Loader2 } from "lucide-react";

interface Question {
  id: number;
  text: string;
  image: string | null;
  option_a: string;
  option_b: string;
  option_c: string;
  option_d: string;
  points: number;
  time_limit_seconds: number;
}

const ExamPage = () => {
  const { examId } = useParams<{ examId: string }>();
  const navigate = useNavigate();
  const { isAuthenticated, user, fetchUserScore } = useAppContext();

  const [questions, setQuestions] = useState<Question[]>([]);
  const [attemptId, setAttemptId] = useState<number | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate("/", { replace: true });
      return;
    }

    const fetchQuestions = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/exams/${examId}/questions/`, {
          headers: {
            'Authorization': `Basic ${btoa(`${user?.username}:${user?.dni}`)}`,
          },
        });
        if (response.ok) {
          const data = await response.json();
          setQuestions(data.questions);
          setAttemptId(data.attempt_id);
        } else {
          console.error("Failed to fetch questions");
        }
      } catch (error) {
        console.error("Error fetching questions:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchQuestions();
  }, [examId, isAuthenticated, navigate, user]);

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-background">
        <Loader2 className="h-8 w-8 animate-spin text-accent mb-4" />
        <p className="text-muted-foreground">Cargando examen...</p>
      </div>
    );
  }

  if (questions.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <p className="text-muted-foreground">No se encontraron preguntas para este examen.</p>
      </div>
    );
  }

  const currentQuestion = questions[currentIndex];

  const handleAnswer = (optionKey: string) => {
    setAnswers((prev) => ({ ...prev, [currentQuestion.id]: optionKey }));
  };

  const handleFinish = async () => {
    if (!attemptId) return;
    setIsSubmitting(true);

    const formattedAnswers = Object.entries(answers).map(([qId, option]) => ({
      question_id: parseInt(qId),
      selected_option: option
    }));

    try {
      const response = await fetch(`http://localhost:8000/api/exams/attempts/${attemptId}/submit_answers/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Basic ${btoa(`${user?.username}:${user?.dni}`)}`,
        },
        body: JSON.stringify({ answers: formattedAnswers }),
      });

      if (response.ok) {
        const data = await response.json();
        setResults(data);
        setShowResults(true);
        fetchUserScore(); // Update points in context
      }
    } catch (error) {
      console.error("Error submitting answers:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (showResults) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center px-4">
        <div className="w-full max-w-lg bg-card rounded-xl border border-border p-8 text-center animate-fade-in">
          <div className="w-16 h-16 rounded-full bg-accent/10 text-accent flex items-center justify-center mx-auto mb-4">
            <CheckCircle2 className="h-8 w-8" />
          </div>
          <h2 className="text-xl font-bold text-foreground mb-1">¡Intento finalizado!</h2>
          <p className="text-sm text-muted-foreground mb-6">
            {results?.counts_for_score ? "Este intento sumó puntos a tu perfil." : "Límite de intentos puntuables alcanzado."}
          </p>

          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="p-4 rounded-lg bg-secondary">
              <p className="text-2xl font-bold text-warning">{results?.score}</p>
              <p className="text-xs text-muted-foreground mt-1">Puntaje obtenido</p>
            </div>
            <div className="p-4 rounded-lg bg-secondary">
              <p className="text-2xl font-bold text-success">{results?.total_user_score}</p>
              <p className="text-xs text-muted-foreground mt-1">Tu puntaje total</p>
            </div>
          </div>

          <div className="flex gap-3">
            <button
              onClick={() => navigate("/dashboard")}
              className="flex-1 py-2.5 rounded-lg border border-border text-sm font-semibold text-foreground hover:bg-secondary transition-colors"
            >
              Volver al dashboard
            </button>
            <button
              onClick={() => window.location.reload()}
              className="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg bg-accent text-accent-foreground text-sm font-semibold hover:opacity-90 transition-opacity"
            >
              <RotateCcw className="h-4 w-4" />
              Nuevo intento
            </button>
          </div>
        </div>
      </div>
    );
  }

  const allAnswered = questions.every((q) => answers[q.id] !== undefined);

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
          <button onClick={() => navigate("/dashboard")} className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors">
            <ArrowLeft className="h-4 w-4" />
            Salir
          </button>
          <span className="text-sm font-medium text-foreground">Examen en progreso</span>
          <span className="text-xs text-muted-foreground">
            {currentIndex + 1} / {questions.length}
          </span>
        </div>
      </header>

      {/* Progress */}
      <div className="max-w-3xl mx-auto px-4 sm:px-6 pt-4">
        <div className="h-1.5 bg-secondary rounded-full overflow-hidden">
          <div
            className="h-full bg-accent rounded-full transition-all duration-300"
            style={{ width: `${((currentIndex + 1) / questions.length) * 100}%` }}
          />
        </div>
      </div>

      {/* Question */}
      <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8">
        <div className="animate-fade-in" key={currentQuestion.id}>
          <span className="inline-block text-xs font-semibold text-accent mb-2 uppercase tracking-wider">
            Pregunta {currentIndex + 1}
          </span>
          <h2 className="text-lg font-semibold text-foreground mb-6">
            {currentQuestion.text}
          </h2>

          <div className="space-y-3">
            {['a', 'b', 'c', 'd'].map((key) => {
              const optionText = (currentQuestion as any)[`option_${key}`];
              const isSelected = answers[currentQuestion.id] === key;
              return (
                <button
                  key={key}
                  onClick={() => handleAnswer(key)}
                  className={`w-full text-left p-4 rounded-lg border text-sm transition-all ${isSelected
                      ? "border-accent bg-accent/5 text-foreground font-medium"
                      : "border-border bg-card text-foreground hover:border-accent/50"
                    }`}
                >
                  <span className={`inline-flex items-center justify-center w-6 h-6 rounded-full text-xs font-semibold mr-3 ${isSelected ? "bg-accent text-accent-foreground" : "bg-secondary text-muted-foreground"
                    }`}>
                    {key.toUpperCase()}
                  </span>
                  {optionText}
                </button>
              );
            })}
          </div>
        </div>

        {/* Navigation */}
        <div className="flex items-center justify-between mt-8">
          <button
            onClick={() => setCurrentIndex((i) => Math.max(0, i - 1))}
            disabled={currentIndex === 0}
            className="flex items-center gap-2 px-4 py-2 rounded-lg border border-border text-sm text-foreground hover:bg-secondary transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
          >
            <ArrowLeft className="h-4 w-4" />
            Anterior
          </button>

          {currentIndex < questions.length - 1 ? (
            <button
              onClick={() => setCurrentIndex((i) => i + 1)}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-accent text-accent-foreground text-sm font-semibold hover:opacity-90 transition-opacity"
            >
              Siguiente
              <ArrowRight className="h-4 w-4" />
            </button>
          ) : (
            <button
              onClick={handleFinish}
              disabled={!allAnswered || isSubmitting}
              className="px-6 py-2 rounded-lg bg-accent text-accent-foreground text-sm font-semibold hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {isSubmitting && <Loader2 className="h-4 w-4 animate-spin" />}
              Finalizar examen
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default ExamPage;
